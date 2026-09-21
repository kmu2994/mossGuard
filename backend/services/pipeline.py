"""
Validation pipeline — orchestrates claim extraction → Moss retrieval → verdict.
Every stage is individually timed with perf_counter.
Computes trust score, risk level, and claim summary statistics.
"""

from __future__ import annotations

import asyncio
import logging
from time import perf_counter

from models import (
    ClaimResult,
    ClaimSummary,
    LatencyBreakdown,
    OverallStatus,
    RiskLevel,
    ValidateResponse,
    Verdict,
)
from services.llm_service import LLMService
from services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)


# ── Trust score weights ────────────────────────────────────────────────

VERDICT_WEIGHTS = {
    Verdict.GROUNDED: 1.0,
    Verdict.UNSUPPORTED: 0.4,
    Verdict.CONTRADICTED: 0.0,
}


def _compute_trust_score(claims: list[ClaimResult]) -> float:
    """
    Compute a weighted trust score (0–100) from claim verdicts and confidences.

    Formula per claim: weight(verdict) × confidence
    Aggregate: mean of all per-claim scores × 100
    """
    if not claims:
        return 100.0

    total = 0.0
    for cr in claims:
        weight = VERDICT_WEIGHTS.get(cr.verdict, 0.0)
        total += weight * cr.confidence
    return round((total / len(claims)) * 100, 1)


def _derive_risk_level(trust_score: float) -> RiskLevel:
    """Map trust score to a risk classification."""
    if trust_score >= 80:
        return RiskLevel.LOW
    elif trust_score >= 60:
        return RiskLevel.MEDIUM
    elif trust_score >= 35:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL


def _build_claim_summary(claims: list[ClaimResult]) -> ClaimSummary:
    """Count claims by verdict type."""
    summary = ClaimSummary()
    for cr in claims:
        if cr.verdict == Verdict.GROUNDED:
            summary.grounded += 1
        elif cr.verdict == Verdict.CONTRADICTED:
            summary.contradicted += 1
        elif cr.verdict == Verdict.UNSUPPORTED:
            summary.unsupported += 1
    return summary


class ValidationPipeline:
    """End-to-end validation pipeline with fine-grained latency tracking."""

    def __init__(
        self, llm: LLMService, retrieval: RetrievalService
    ) -> None:
        self._llm = llm
        self._retrieval = retrieval

    async def _retrieve_for_claim(
        self, claim: str
    ) -> tuple[list[str], float]:
        """Retrieve context for a single claim. Returns (texts, latency_ms)."""
        t0 = perf_counter()
        results = await self._retrieval.search(claim, top_k=3)
        latency_ms = (perf_counter() - t0) * 1000
        texts = [r.text for r in results]
        return texts, latency_ms

    async def _classify_claim(
        self, claim: str, contexts: list[str]
    ) -> tuple[str, float, str, float]:
        """Classify a claim. Returns (verdict, confidence, reason, latency_ms)."""
        t0 = perf_counter()
        result = await self._llm.classify_claim(claim, contexts)
        latency_ms = (perf_counter() - t0) * 1000
        return result.verdict, result.confidence, result.reason, latency_ms

    async def _process_single_claim(self, claim: str) -> ClaimResult:
        """Run retrieval + classification for one claim safely."""
        try:
            # Step 1: Retrieve
            contexts, retrieval_ms = await self._retrieve_for_claim(claim)

            # Step 2: Classify
            verdict, confidence, reason, verdict_ms = await self._classify_claim(
                claim, contexts
            )

            return ClaimResult(
                claim=claim,
                verdict=Verdict(verdict),
                confidence=confidence,
                reason=reason,
                matched_context=contexts,
                retrieval_latency_ms=round(retrieval_ms, 2),
                verdict_latency_ms=round(verdict_ms, 2),
            )
        except Exception as exc:
            logger.error("Error processing claim '%s': %s", claim, exc)
            return ClaimResult(
                claim=claim,
                verdict=Verdict.UNSUPPORTED,
                confidence=0.0,
                reason=f"Processing fallback: {exc}",
                matched_context=[],
                retrieval_latency_ms=0.0,
                verdict_latency_ms=0.0,
            )

    async def validate(self, text: str) -> ValidateResponse:
        """
        Full validation pipeline:
          1. Extract claims (LLM)
          2. For each claim: retrieve context (Moss) + classify (LLM)
          3. Aggregate results, latency breakdown, trust score, and risk level
        """
        pipeline_start = perf_counter()

        # ── Stage 1: Claim extraction ──────────────────────────────────
        t0 = perf_counter()
        claims = await self._llm.extract_claims(text)
        extraction_ms = (perf_counter() - t0) * 1000
        logger.info(
            "Extracted %d claims in %.1fms", len(claims), extraction_ms
        )

        if not claims:
            total_ms = (perf_counter() - pipeline_start) * 1000
            return ValidateResponse(
                claims=[],
                latency_breakdown=LatencyBreakdown(
                    extraction_ms=round(extraction_ms, 2),
                    total_retrieval_ms=0.0,
                    total_verdict_ms=0.0,
                    total_ms=round(total_ms, 2),
                ),
                overall_status=OverallStatus.SAFE,
                trust_score=100.0,
                risk_level=RiskLevel.LOW,
                claim_summary=ClaimSummary(),
            )

        # ── Stage 2+3: Retrieval + classification (parallel) ──────────
        claim_results = await asyncio.gather(
            *(self._process_single_claim(c) for c in claims)
        )

        # ── Aggregate latencies ────────────────────────────────────────
        total_retrieval_ms = sum(cr.retrieval_latency_ms for cr in claim_results)
        total_verdict_ms = sum(cr.verdict_latency_ms for cr in claim_results)
        total_ms = (perf_counter() - pipeline_start) * 1000

        # ── Determine overall status ───────────────────────────────────
        has_contradiction = any(
            cr.verdict == Verdict.CONTRADICTED for cr in claim_results
        )
        overall_status = (
            OverallStatus.UNSAFE if has_contradiction else OverallStatus.SAFE
        )

        # ── Compute enhanced guardrail metrics ─────────────────────────
        claim_results_list = list(claim_results)
        trust_score = _compute_trust_score(claim_results_list)
        risk_level = _derive_risk_level(trust_score)
        claim_summary = _build_claim_summary(claim_results_list)

        logger.info(
            "Validation complete — trust=%.1f risk=%s claims=%d (G:%d C:%d U:%d)",
            trust_score, risk_level.value, len(claim_results_list),
            claim_summary.grounded, claim_summary.contradicted, claim_summary.unsupported,
        )

        return ValidateResponse(
            claims=claim_results_list,
            latency_breakdown=LatencyBreakdown(
                extraction_ms=round(extraction_ms, 2),
                total_retrieval_ms=round(total_retrieval_ms, 2),
                total_verdict_ms=round(total_verdict_ms, 2),
                total_ms=round(total_ms, 2),
            ),
            overall_status=overall_status,
            trust_score=trust_score,
            risk_level=risk_level,
            claim_summary=claim_summary,
        )
