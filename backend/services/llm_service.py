"""
Provider-agnostic LLM service for claim extraction and verdict classification.
Currently uses OpenAI but the interface is designed for easy swapping.
"""

from __future__ import annotations

import json
import logging
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


# ── Prompt templates ───────────────────────────────────────────────────

EXTRACT_CLAIMS_PROMPT = """You are a factual claim extractor. Given a block of text, extract every discrete, checkable factual claim.

Rules:
- Each claim must be a single, self-contained statement that can be independently verified.
- Do NOT include opinions, subjective statements, or vague generalizations.
- Do NOT include filler like "The company says..." — just the factual assertion.
- Return ONLY a JSON array of strings — no markdown, no explanation.

Text:
\"\"\"
{text}
\"\"\"

Output:"""

CLASSIFY_CLAIM_PROMPT = """You are a fact-checking classifier. Given a factual claim and a list of context passages from a trusted knowledge base, classify the claim.

Claim:
\"\"\"{claim}\"\"\"

Context passages from knowledge base:
{contexts}

Classify the claim as one of:
- "grounded": The claim is clearly supported by the context passages.
- "contradicted": The claim is explicitly refuted or contradicted by the context passages.
- "unsupported": The context passages do not contain enough information to verify or refute the claim.

Return ONLY a JSON object with exactly these keys:
- "verdict": one of "grounded", "contradicted", "unsupported"
- "confidence": a float between 0.0 and 1.0 indicating your confidence
- "reason": one short sentence explaining your classification

Output:"""


# ── LLM Service ────────────────────────────────────────────────────────

class LLMService:
    """Thin wrapper around an LLM provider for claim extraction and verdict."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.LLM_BASE_URL or None,
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
        prompt = EXTRACT_CLAIMS_PROMPT.format(text=text)
        raw = await self._chat(prompt)

        # Strip markdown code fences if the model wraps its output
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        try:
            claims = json.loads(raw)
            if isinstance(claims, list):
                return [str(c) for c in claims if c]
        except json.JSONDecodeError:
            logger.warning("Failed to parse claims JSON: %s", raw[:200])

        return []

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

        try:
            data = json.loads(raw)
            return ClaimVerdict(
                verdict=data.get("verdict", "unsupported"),
                confidence=float(data.get("confidence", 0.5)),
                reason=data.get("reason", "Unable to determine."),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            logger.warning("Failed to parse verdict JSON: %s — %s", raw[:200], exc)
            return ClaimVerdict(
                verdict="unsupported",
                confidence=0.0,
                reason="LLM returned an unparseable response.",
            )
