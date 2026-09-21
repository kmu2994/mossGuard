"""
Moss retrieval service — handles index loading and semantic search.
Uses moss_core IndexManager with fallback local in-memory search for sub-10ms performance.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any

from config import get_settings

logger = logging.getLogger(__name__)

# Pre-populated knowledge base fallback documents
DEFAULT_DOCUMENTS = [
    {
        "id": "pricing-free",
        "text": "CloudVault offers a Free tier at $0/month with 5 GB storage, 1 user seat, and community-only support.",
    },
    {
        "id": "pricing-pro",
        "text": "CloudVault Pro costs $29/month per user and includes 100 GB storage, priority email support with a 4-hour response SLA, and API access.",
    },
    {
        "id": "pricing-enterprise",
        "text": "CloudVault Enterprise costs $149/month per user and includes unlimited storage, a 1-hour support response SLA, dedicated account manager, and SSO integration.",
    },
    {
        "id": "refund-policy",
        "text": "CloudVault offers a 30-day money-back guarantee on all paid plans. Refund requests made after 30 days from the billing date are not eligible for a refund under any circumstances.",
    },
    {
        "id": "refund-process",
        "text": "Refunds are processed within 5-7 business days after approval. Contact billing@cloudvault.io to initiate a refund request.",
    },
    {
        "id": "support-free",
        "text": "CloudVault Free tier includes community forum support only. Free-tier users do NOT have access to phone support, email support, or any dedicated support channels.",
    },
    {
        "id": "support-pro",
        "text": "CloudVault Pro includes priority email support with a guaranteed 4-hour initial response time during business hours (9 AM – 6 PM EST, Monday–Friday).",
    },
    {
        "id": "support-enterprise",
        "text": "CloudVault Enterprise includes 24/7 phone and email support with a guaranteed 1-hour initial response time and a dedicated account manager.",
    },
    {
        "id": "security-encryption",
        "text": "CloudVault encrypts all data at rest using AES-256 encryption. CloudVault does NOT offer end-to-end encryption. Data is encrypted in transit using TLS 1.3.",
    },
    {
        "id": "security-compliance",
        "text": "CloudVault is SOC 2 Type II certified and GDPR compliant. CloudVault is NOT HIPAA compliant and should not be used to store protected health information (PHI).",
    },
    {
        "id": "security-2fa",
        "text": "Two-factor authentication (2FA) is available on all CloudVault plans, including the Free tier. Supported methods are TOTP authenticator apps and SMS.",
    },
    {
        "id": "uptime-sla",
        "text": "CloudVault guarantees 99.9% uptime for Pro and Enterprise plans. The Free tier has no uptime SLA. CloudVault does NOT guarantee 99.99% uptime on any plan.",
    },
    {
        "id": "data-retention",
        "text": "Deleted files in CloudVault are retained in the trash for 30 days before permanent deletion. Enterprise plans can configure custom retention periods up to 1 year.",
    },
    {
        "id": "api-rate-limits",
        "text": "CloudVault API rate limits are: Free tier — 100 requests/hour, Pro — 10,000 requests/hour, Enterprise — 100,000 requests/hour. Rate-limited requests receive a 429 HTTP status code.",
    },
    {
        "id": "data-export",
        "text": "CloudVault supports data export in CSV, JSON, and ZIP formats. Full account exports can be requested from the Settings page and are available for download within 24 hours.",
    },
    {
        "id": "integrations",
        "text": "CloudVault integrates with Slack, Microsoft Teams, Jira, and Zapier. A public REST API and webhooks are available on Pro and Enterprise plans.",
    },
    {
        "id": "trial-period",
        "text": "CloudVault offers a 14-day free trial of the Pro plan. No credit card is required to start the trial. After the trial ends, the account automatically downgrades to the Free tier.",
    },
    {
        "id": "storage-limits",
        "text": "CloudVault storage limits are strictly enforced. Users who exceed their plan's storage limit will receive a warning and have 7 days to reduce usage before uploads are disabled.",
    },
]


@dataclass
class SearchResult:
    """A single document match from Moss."""
    id: str
    text: str
    score: float


class RetrievalService:
    """Wraps Moss index manager for sub-10ms queries with resilient fallback."""

    def __init__(self) -> None:
        settings = get_settings()
        self._project_id = settings.MOSS_PROJECT_ID
        self._project_key = settings.MOSS_PROJECT_KEY
        self._index_name = settings.MOSS_INDEX_NAME
        self._manager: Any = None
        self._loaded = False
        self._local_docs = DEFAULT_DOCUMENTS

    async def load_index(self) -> None:
        """Pull the index into local memory for sub-10ms queries."""
        logger.info("Loading Moss index '%s' into memory...", self._index_name)
        try:
            from moss_core import IndexManager
            self._manager = IndexManager(self._project_id, self._project_key)
            self._manager.load_index(self._index_name)
            self._loaded = True
            logger.info("Moss index '%s' loaded into memory successfully.", self._index_name)
        except Exception as exc:
            logger.warning("Moss cloud index load failed: %s. Using local in-memory search.", exc)
            self._loaded = True

    def _score_local(self, query: str, text: str) -> float:
        """Compute keyword + token overlap score between query and document text."""
        q_tokens = set(re.findall(r'\w+', query.lower()))
        t_tokens = set(re.findall(r'\w+', text.lower()))
        if not q_tokens:
            return 0.0
        intersection = q_tokens.intersection(t_tokens)
        return len(intersection) / float(len(q_tokens))

    async def search(
        self, query: str, top_k: int = 3, alpha: float = 0.8
    ) -> list[SearchResult]:
        """
        Query the loaded Moss index.

        Args:
            query: The search query text.
            top_k: Number of top results to return.
            alpha: Balance between semantic and keyword matching.

        Returns:
            List of SearchResult with id, text, and relevance score.
        """
        if not self._loaded:
            await self.load_index()

        if self._manager is not None:
            try:
                raw_results = self._manager.query_text(
                    self._index_name, query, top_k=top_k, alpha=alpha
                )
                return [
                    SearchResult(
                        id=getattr(res, "id", str(i)),
                        text=getattr(res, "text", str(res)),
                        score=float(getattr(res, "score", 0.9)),
                    )
                    for i, res in enumerate(raw_results)
                ]
            except Exception as exc:
                logger.debug("Moss index manager query failed: %s — using local fallback", exc)

        # Local in-memory high speed search fallback
        scored = []
        for doc in self._local_docs:
            score = self._score_local(query, doc["text"])
            if score > 0:
                scored.append(SearchResult(id=doc["id"], text=doc["text"], score=round(score, 3)))

        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]
