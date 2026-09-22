"""
LiveKit Service — Real-time WebRTC stream evaluation & voice guardrails.
Generates signed WebRTC access tokens and processes transcribed LiveKit audio streams.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta

import importlib

jwt: any = None
try:
    jwt = importlib.import_module("jwt")
except ImportError:
    pass

if jwt is None:
    import base64
    import hashlib
    import hmac
    import json

    class _JWTFallback:
        @staticmethod
        def encode(payload: dict, key: str, algorithm: str = "HS256") -> str:
            header = {"alg": algorithm, "typ": "JWT"}
            h_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
            p_b64 = base64.urlsafe_b64encode(json.dumps(payload, default=str).encode()).decode().rstrip("=")
            signing_input = f"{h_b64}.{p_b64}".encode()
            sig = hmac.new(key.encode(), signing_input, hashlib.sha256).digest()
            sig_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
            return f"{h_b64}.{p_b64}.{sig_b64}"

    jwt = _JWTFallback()

from config import get_settings
from models import LiveKitStreamRequest, LiveKitStreamResponse, ValidateResponse
from services.pipeline import ValidationPipeline

logger = logging.getLogger(__name__)


class LiveKitService:
    """Orchestrates LiveKit WebRTC tokens and real-time voice stream guardrails."""

    def __init__(self, pipeline: ValidationPipeline) -> None:
        self._pipeline = pipeline
        self._settings = get_settings()

    def generate_token(self, room_name: str, identity: str) -> tuple[str, str]:
        """
        Generate a signed WebRTC access token for LiveKit room sessions.
        Returns (access_token, livekit_url).
        """
        api_key = self._settings.LIVEKIT_API_KEY
        api_secret = self._settings.LIVEKIT_API_SECRET
        livekit_url = self._settings.LIVEKIT_URL

        now = int(time.time())
        exp = now + 3600  # 1 hour validity

        payload = {
            "iss": api_key,
            "sub": identity,
            "exp": exp,
            "nbf": now - 5,
            "video": {
                "room": room_name,
                "roomJoin": True,
                "canPublish": True,
                "canSubscribe": True,
                "canPublishData": True,
            },
            "metadata": "mossguard-realtime-voice-guardrail",
        }

        token = jwt.encode(payload, api_secret, algorithm="HS256")
        logger.info("Generated LiveKit WebRTC token for room '%s' identity '%s'", room_name, identity)
        return token, livekit_url

    async def process_audio_stream(
        self, req: LiveKitStreamRequest
    ) -> LiveKitStreamResponse:
        """
        Process a real-time transcribed audio stream chunk from a LiveKit WebRTC session.
        Feeds transcript into MossGuard pipeline and wraps response with stream metadata.
        """
        t0 = time.perf_counter()
        validate_res: ValidateResponse = await self._pipeline.validate(req.transcript)
        audio_ms = round((time.perf_counter() - t0) * 1000, 2)

        return LiveKitStreamResponse(
            claims=validate_res.claims,
            latency_breakdown=validate_res.latency_breakdown,
            overall_status=validate_res.overall_status,
            trust_score=validate_res.trust_score,
            risk_level=validate_res.risk_level,
            claim_summary=validate_res.claim_summary,
            trace_id=validate_res.trace_id,
            is_live_stream=True,
            speaker_id=req.speaker_id,
            audio_latency_ms=audio_ms,
        )
