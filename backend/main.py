"""
MossGuard API — Real-time AI agent trust & guardrail system.

Run with:
    uvicorn main:app --reload
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from models import ValidateRequest, ValidateResponse
from services.llm_service import LLMService
from services.retrieval_service import RetrievalService
from services.pipeline import ValidationPipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ── Service singletons (initialised in lifespan) ──────────────────────

llm_service: LLMService | None = None
retrieval_service: RetrievalService | None = None
pipeline: ValidationPipeline | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: load Moss index into memory. Shutdown: cleanup."""
    global llm_service, retrieval_service, pipeline

    settings = get_settings()
    logger.info("Initialising MossGuard services...")
    logger.info("  Moss index : %s", settings.MOSS_INDEX_NAME)
    logger.info("  LLM model  : %s", settings.LLM_MODEL)

    llm_service = LLMService()
    retrieval_service = RetrievalService()

    try:
        await retrieval_service.load_index()
        logger.info("Moss index loaded — ready to serve requests.")
    except Exception as exc:
        logger.error("Failed to load Moss index: %s", exc)
        logger.warning(
            "Server starting WITHOUT Moss index. "
            "Run seed_kb.py first, then restart."
        )

    pipeline = ValidationPipeline(llm_service, retrieval_service)

    yield  # app is running

    logger.info("Shutting down MossGuard.")


# ── FastAPI app ────────────────────────────────────────────────────────

app = FastAPI(
    title="MossGuard",
    description="Real-time AI agent trust & guardrail system",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — wide open for hackathon demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ─────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Basic health check."""
    return {"status": "ok", "service": "mossguard"}


@app.post("/v1/validate", response_model=ValidateResponse)
async def validate(req: ValidateRequest):
    """
    Validate an AI agent's text response.

    Pipeline:
      1. Extract factual claims (LLM)
      2. Retrieve supporting context per claim (Moss)
      3. Classify each claim as grounded / contradicted / unsupported (LLM)
    """
    global pipeline
    if pipeline is None:
        logger.info("Initializing MossGuard pipeline on demand...")
        llm_svc = LLMService()
        retrieval_svc = RetrievalService()
        try:
            await retrieval_svc.load_index()
        except Exception as exc:
            logger.warning("Moss index load warning: %s", exc)
        pipeline = ValidationPipeline(llm_svc, retrieval_svc)
    return await pipeline.validate(req.text)
