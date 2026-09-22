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
    trace_id: str = Field(default="trace-moss-001", description="OpenTelemetry request trace identifier.")


# ── Auth & LiveKit Models ───────────────────────────────────────────────

class AuthTokenRequest(BaseModel):
    client_id: str = Field(..., description="OAuth2 client identifier.")
    client_secret: str = Field(..., description="OAuth2 client secret key.")


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600


class LiveKitTokenRequest(BaseModel):
    room_name: str = Field(default="mossguard-voice-room", description="LiveKit WebRTC room name.")
    identity: str = Field(default="user-agent-01", description="Client participant identity.")


class LiveKitTokenResponse(BaseModel):
    token: str = Field(..., description="Signed LiveKit WebRTC access token.")
    url: str = Field(..., description="LiveKit WebRTC server WebSocket URL.")
    room_name: str
    identity: str


class LiveKitStreamRequest(BaseModel):
    transcript: str = Field(..., description="Real-time transcribed audio text chunk from LiveKit WebRTC stream.")
    room_name: str = Field(default="mossguard-voice-room")
    speaker_id: str = Field(default="agent-speaker")


class LiveKitStreamResponse(ValidateResponse):
    is_live_stream: bool = True
    speaker_id: str = "agent-speaker"
    audio_latency_ms: float = 1.2


class SecurityAuditInfo(BaseModel):
    oauth2_jwt_enabled: bool = True
    rate_limiting_enabled: bool = True
    rate_limit_per_minute: int = 60
    encryption_at_rest: str = "AES-256"
    encryption_in_transit: str = "TLS 1.3"
    prompt_engineering_standard: str = "CRISPE"
    opentelemetry_enabled: bool = True
