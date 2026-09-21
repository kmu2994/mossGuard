"""
Pydantic request/response schemas for the MossGuard API.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────

class Verdict(str, Enum):
    GROUNDED = "grounded"
    CONTRADICTED = "contradicted"
    UNSUPPORTED = "unsupported"


class OverallStatus(str, Enum):
    SAFE = "safe"
    UNSAFE = "unsafe"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ── Request ────────────────────────────────────────────────────────────

class ValidateRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The AI agent's text response to validate.")


# ── Response ───────────────────────────────────────────────────────────

class ClaimResult(BaseModel):
    claim: str
    verdict: Verdict
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str
    matched_context: list[str] = Field(default_factory=list)
    retrieval_latency_ms: float
    verdict_latency_ms: float


class LatencyBreakdown(BaseModel):
    extraction_ms: float
    total_retrieval_ms: float
    total_verdict_ms: float
    total_ms: float


class ClaimSummary(BaseModel):
    grounded: int = 0
    contradicted: int = 0
    unsupported: int = 0


class ValidateResponse(BaseModel):
    claims: list[ClaimResult]
    latency_breakdown: LatencyBreakdown
    overall_status: OverallStatus
    trust_score: float = Field(
        ..., ge=0.0, le=100.0,
        description="Aggregate trust score (0–100) based on claim verdicts and confidences."
    )
    risk_level: RiskLevel = Field(
        ..., description="Risk classification: low / medium / high / critical."
    )
    claim_summary: ClaimSummary = Field(
        ..., description="Count of claims by verdict type."
    )
