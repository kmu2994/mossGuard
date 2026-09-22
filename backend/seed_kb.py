"""
Seed the Moss knowledge base with sample facts about CloudVault (a fictional SaaS product).

Usage:
    python seed_kb.py

Requires MOSS_PROJECT_ID, MOSS_PROJECT_KEY, and MOSS_INDEX_NAME env vars
(or a .env file in the same directory).
"""

import asyncio
import os
import sys

from dotenv import load_dotenv



from moss import MossClient

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────

PROJECT_ID = os.getenv("MOSS_PROJECT_ID")
PROJECT_KEY = os.getenv("MOSS_PROJECT_KEY")
INDEX_NAME = os.getenv("MOSS_INDEX_NAME", "mossguard-kb")

# ── Knowledge Base Documents ───────────────────────────────────────────

DOCUMENTS = [
    # Pricing
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
    # Refund policy
    {
        "id": "refund-policy",
        "text": "CloudVault offers a 30-day money-back guarantee on all paid plans. Refund requests made after 30 days from the billing date are not eligible for a refund under any circumstances.",
    },
    {
        "id": "refund-process",
        "text": "Refunds are processed within 5-7 business days after approval. Contact billing@cloudvault.io to initiate a refund request.",
    },
    # Support SLAs
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
    # Security — CONTRADICTION BAIT
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
    # Uptime — CONTRADICTION BAIT
    {
        "id": "uptime-sla",
        "text": "CloudVault guarantees 99.9% uptime for Pro and Enterprise plans. The Free tier has no uptime SLA. CloudVault does NOT guarantee 99.99% uptime on any plan.",
    },
    # Data retention
    {
        "id": "data-retention",
        "text": "Deleted files in CloudVault are retained in the trash for 30 days before permanent deletion. Enterprise plans can configure custom retention periods up to 1 year.",
    },
    # API limits
    {
        "id": "api-rate-limits",
        "text": "CloudVault API rate limits are: Free tier — 100 requests/hour, Pro — 10,000 requests/hour, Enterprise — 100,000 requests/hour. Rate-limited requests receive a 429 HTTP status code.",
    },
    # Data export
    {
        "id": "data-export",
        "text": "CloudVault supports data export in CSV, JSON, and ZIP formats. Full account exports can be requested from the Settings page and are available for download within 24 hours.",
    },
    # Integrations
    {
        "id": "integrations",
        "text": "CloudVault integrates with Slack, Microsoft Teams, Jira, and Zapier. A public REST API and webhooks are available on Pro and Enterprise plans.",
    },
    # Trial
    {
        "id": "trial-period",
        "text": "CloudVault offers a 14-day free trial of the Pro plan. No credit card is required to start the trial. After the trial ends, the account automatically downgrades to the Free tier.",
    },
    # Storage
    {
        "id": "storage-limits",
        "text": "CloudVault storage limits are strictly enforced. Users who exceed their plan's storage limit will receive a warning and have 7 days to reduce usage before uploads are disabled.",
    },
]


async def main():
    if not PROJECT_ID or not PROJECT_KEY:
        print("ERROR: Set MOSS_PROJECT_ID and MOSS_PROJECT_KEY in your .env file.")
        sys.exit(1)

    client = MossClient(PROJECT_ID, PROJECT_KEY)

    print(f"Creating Moss index '{INDEX_NAME}' with {len(DOCUMENTS)} documents...")

    try:
        await client.create_index(INDEX_NAME, DOCUMENTS)
        print(f"✓ Index '{INDEX_NAME}' created and documents uploaded.")
    except Exception as exc:
        # Index might already exist — try to log what went wrong
        print(f"Note: {exc}")
        print("If the index already exists, you can delete and re-create it, or skip this step.")

    # Warm the index by loading it
    print("Loading index into memory to verify...")
    await client.load_index(INDEX_NAME)
    print("✓ Index loaded into memory successfully.")

    # Run a quick test query
    from moss import QueryOptions
    results = await client.query(
        INDEX_NAME,
        "Does CloudVault offer end-to-end encryption?",
        QueryOptions(top_k=3),
    )
    print("\nTest query: 'Does CloudVault offer end-to-end encryption?'")
    for doc in results.docs:
        print(f"  [{doc.score:.3f}] {doc.text[:100]}...")

    print(f"\n✓ Knowledge base seeded successfully with {len(DOCUMENTS)} facts.")
    print("  You can now start the server with: uvicorn main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())
