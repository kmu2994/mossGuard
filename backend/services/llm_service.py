"""
Provider-agnostic LLM service for claim extraction and verdict classification.
Includes rate-limit resilience and heuristic fallbacks to guarantee 100% server uptime.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass

from openai import AsyncOpenAI

from config import get_settings

logger = logging.getLogger(__name__)

# ── Data classes ───────────────────────────────────────────────────────

@dataclass
class ClaimVerdict:
    verdict: str          # "grounded" | "contradicted" | "unsupported"
    confidence: float     # 0.0 – 1.0
    reason: str           # one short sentence


# ── CRISPE Prompt Engineering Templates ──────────────────────────────────

EXTRACT_CLAIMS_PROMPT = """[CAPACITY] You are operating as an elite Enterprise AI Compliance Auditor and Claim Extraction Engine.
[ROLE] Your role is to isolate every discrete, checkable factual assertion from AI agent text streams.
[INSIGHT] Background: AI agent outputs frequently blend legitimate facts with hallucinations (fake pricing, non-existent SLA guarantees, unauthorized HIPAA or E2E encryption claims).
[STATEMENT] Instructions: Extract every checkable statement as a self-contained factual assertion. Exclude subjective filler, greetings, or marketing opinions.
[PERSONALITY] Objective, unemotional, highly analytical, and strictly neutral.
[EXPERIMENT / FORMAT] Output Format: Return ONLY a valid raw JSON array of strings containing the claims. Do not include markdown codeblocks or explanatory text.

Input Text:
\"\"\"
{text}
\"\"\"

JSON Array Output:"""

CLASSIFY_CLAIM_PROMPT = """[CAPACITY] You are operating as a Senior Fact-Verification Judge & Compliance Engine.
[ROLE] Your role is to evaluate a single factual claim against context passages retrieved from a trusted knowledge base.
[INSIGHT] Context Passages from Knowledge Base:
{contexts}

Target Claim:
\"\"\"{claim}\"\"\"

[STATEMENT] Classification Instructions:
- "grounded": The claim is explicitly confirmed by the retrieved context passages.
- "contradicted": The claim is explicitly refuted or contradicted by the retrieved context passages.
- "unsupported": The retrieved context passages contain insufficient evidence to confirm or refute the claim.

[PERSONALITY] Rigorous, evidence-based, zero-hallucination, and exact.
[EXPERIMENT / FORMAT] Output Format: Return ONLY a raw JSON object with keys:
- "verdict": "grounded" | "contradicted" | "unsupported"
- "confidence": float between 0.0 and 1.0
- "reason": one concise sentence explaining the evidence-based classification

JSON Object Output:"""


# ── LLM Service ────────────────────────────────────────────────────────

class LLMService:
    """Thin wrapper around an LLM provider for claim extraction and verdict."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(
            api_key=settings.api_key,
            base_url=settings.LLM_BASE_URL or None,
            max_retries=0,
            timeout=10.0,
        )
        self._model = settings.LLM_MODEL

    async def _chat(self, prompt: str, temperature: float = 0.0) -> str:
        """Send a single-turn chat completion and return the content."""
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=2048,
        )
        return response.choices[0].message.content.strip()

    async def extract_claims(self, text: str) -> list[str]:
        """Extract discrete factual claims from the given text."""
        try:
            prompt = EXTRACT_CLAIMS_PROMPT.format(text=text)
            raw = await self._chat(prompt)

            # Strip markdown code fences if the model wraps its output
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()

            claims = json.loads(raw)
            if isinstance(claims, list) and claims:
                return [str(c) for c in claims if c]
        except Exception as exc:
            logger.warning("LLM claim extraction failed/rate-limited (%s). Using sentence fallback.", exc)

        # Fallback: split text into clean sentence claims
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 10]
        return sentences or [text.strip()]

    async def classify_claim(
        self, claim: str, contexts: list[str]
    ) -> ClaimVerdict:
        """Classify a single claim against retrieved context passages."""
        if not contexts:
            return ClaimVerdict(
                verdict="unsupported",
                confidence=0.9,
                reason="No relevant context found in the knowledge base.",
            )

        try:
            formatted_contexts = "\n".join(
                f"  [{i + 1}] {ctx}" for i, ctx in enumerate(contexts)
            )
            prompt = CLASSIFY_CLAIM_PROMPT.format(
                claim=claim, contexts=formatted_contexts
            )
            raw = await self._chat(prompt)

            # Strip markdown code fences
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
                if raw.endswith("```"):
                    raw = raw[:-3]
                raw = raw.strip()

            data = json.loads(raw)
            return ClaimVerdict(
                verdict=data.get("verdict", "unsupported"),
                confidence=float(data.get("confidence", 0.5)),
                reason=data.get("reason", "Unable to determine."),
            )
        except Exception as exc:
            logger.warning("LLM claim classification failed/rate-limited (%s). Using heuristic fallback.", exc)
            return self._heuristic_classify(claim, contexts)

    def _heuristic_classify(self, claim: str, contexts: list[str]) -> ClaimVerdict:
        """Rule-based heuristic classifier fallback when LLM API is rate-limited or fails."""
        claim_lower = claim.lower()
        combined_ctx = " ".join(contexts).lower()

        # Check for negation mismatch
        negations = ["not ", "no ", "never ", "does not ", "is not "]
        has_claim_negation = any(neg in claim_lower for neg in negations)
        has_ctx_negation = any(neg in combined_ctx for neg in negations)

        # Basic word match overlap
        claim_words = set(re.findall(r'\b\w{3,}\b', claim_lower))
        ctx_words = set(re.findall(r'\b\w{3,}\b', combined_ctx))
        overlap = claim_words.intersection(ctx_words)

        if len(overlap) >= max(1, len(claim_words) * 0.4):
            if has_claim_negation != has_ctx_negation and ("not" in combined_ctx or "not" in claim_lower):
                return ClaimVerdict(
                    verdict="contradicted",
                    confidence=0.85,
                    reason="Matched context indicates a contradiction with the claim.",
                )
            return ClaimVerdict(
                verdict="grounded",
                confidence=0.85,
                reason="Claim is supported by matched knowledge base context.",
            )

        return ClaimVerdict(
            verdict="unsupported",
            confidence=0.7,
            reason="Insufficient evidence in knowledge base context to verify claim.",
        )

