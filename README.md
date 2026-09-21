# 🛡️ MossGuard

**Real-time AI agent trust & guardrail system** — catches hallucinations by fact-checking claims against a knowledge base using [Moss](https://moss.dev) for sub-10ms semantic retrieval.

![MossGuard Dashboard](https://img.shields.io/badge/Status-Hackathon_Submission-brightgreen?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=nextdotjs)
![Moss](https://img.shields.io/badge/Moss-Sub--10ms_Retrieval-7C3AED?style=for-the-badge)

---

## ⚡ The Key Differentiator: Sub-10ms Retrieval with Moss

In production AI agent guardrails, latency is the bottleneck. Traditional RAG systems require multi-stage network hops to remote vector databases, adding **150ms – 400ms** per retrieval call. When validating multiple extracted claims sequentially or in batch, guardrail latency quickly exceeds 1 second, making real-time user-facing validation impossible.

**MossGuard solves this by utilizing Moss's in-memory index loaded directly into local process memory.**

| Metric | Traditional Vector DB | Moss In-Memory Index (MossGuard) |
|---|---|---|
| **Query Latency** | 150ms – 400ms | **< 10ms (Typically 1.5ms – 4.5ms)** |
| **Network Hops** | External HTTP / gRPC call | Local in-memory index query |
| **Real-time Viability** | High overhead for multi-claim agent responses | **Seamless inline validation before response delivery** |
| **Parallel Retrieval** | High tail-latency amplification | Multi-claim parallel retrieval in single-digit ms |

---

## 📐 Architecture Diagram

```mermaid
flowchart TD
    subgraph Client ["Client Layer"]
        UI["Next.js 15 Dashboard<br/>(React / TypeScript)"]
    end

    subgraph API ["API & Orchestration Layer"]
        FastAPI["FastAPI Backend Server<br/>(Python 3.11 / Uvicorn)"]
        Pipeline["Validation Pipeline<br/>(Async Orchestration)"]
    end

    subgraph Core ["Processing & Retrieval Core"]
        LLM_Extract["LLM Claim Extractor<br/>(GPT-4o-mini)"]
        MossIndex[("Moss In-Memory KB<br/>Sub-10ms Semantic Index")]
        LLM_Classify["LLM Verdict Classifier<br/>(Grounded / Contradicted / Unsupported)"]
    end

    UI -->|"POST /v1/validate"| FastAPI
    FastAPI --> Pipeline
    Pipeline -->|"Step 1: Extract discrete claims"| LLM_Extract
    LLM_Extract -->|"Claims Array"| Pipeline
    Pipeline -->|"Step 2: Concurrent query (Sub-10ms)"| MossIndex
    MossIndex -->|"Matched Context Passages"| Pipeline
    Pipeline -->|"Step 3: Fact-check claim vs context"| LLM_Classify
    LLM_Classify -->|"Verdict + Confidence + Reason"| Pipeline
    Pipeline -->|"ValidateResponse JSON + Latency Breakdown"| UI
```

---

## 📋 Product Requirements Document (PRD)

### 1. Executive Summary & Problem Statement
Large Language Model (LLM) agents are increasingly deployed in customer-facing and mission-critical roles (customer support, medical assistance, enterprise software). However, LLMs regularly generate **hallucinations**—statements that sound convincing but contradict internal product docs, SLAs, or security guidelines.

Existing guardrail approaches rely on heavy post-processing or remote vector database roundtrips, introducing high latency that breaks real-time user experience. **MossGuard** provides real-time, fine-grained fact verification by pairing LLM extraction and classification with **Moss's sub-10ms in-memory vector search**, stopping hallucinated claims in their tracks.

### 2. Core User Experience & Workflow
1. **Input Agent Text**: The user/system submits an AI agent's generated response to MossGuard.
2. **Discrete Claim Extraction**: An LLM parses the block of text and isolates checkable factual statements (e.g. pricing figures, SLA guarantees, security features), excluding subjective opinions.
3. **Sub-10ms Context Retrieval**: For each extracted claim, Moss retrieves the most relevant context passages from the local in-memory index in **under 10ms**.
4. **Verdict Classification**: The claim is compared against the retrieved context passages to render a verdict:
   - 🟢 **Grounded**: Verified by knowledge base content.
   - 🔴 **Contradicted**: Explicitly refuted by knowledge base content (hallucination caught).
   - 🟡 **Unsupported**: Information not present in knowledge base.
5. **Real-time Diagnostics**: The dashboard renders individual claim cards, confidence scores, source context excerpts, and a latency breakdown bar highlighting Moss's ultra-low retrieval overhead.

### 3. Key Functional & Technical Requirements
- **Sub-10ms Retrieval SLA**: All Moss index queries must execute within <10ms to ensure end-to-end responsiveness.
- **Provider-Agnostic Abstraction**: LLM interface cleanly decoupled to allow swapping providers (OpenAI, Anthropic, local models).
- **Concurrent Processing**: Multi-claim retrieval and verdict classification must execute concurrently using Python `asyncio.gather`.
- **Transparent Diagnostics**: Every response includes per-stage latency timings (`extraction_ms`, `total_retrieval_ms`, `total_verdict_ms`, `total_ms`).
- **Resilient Fallbacks**: Graceful handling of missing context or unparseable model responses without crashing the pipeline.

### 4. Non-Functional Requirements
- **Security**: No raw prompt injection exposure; claims strictly evaluated against trusted knowledge base passages.
- **Scalability**: In-memory retrieval scale allows thousands of queries per second per process.
- **Usability**: High-contrast, glassmorphic dark mode dashboard with zero-config sample loading for fast hackathon judging.

---

## 📁 Project Structure

```
mossGuard/
├── backend/                 # FastAPI Python backend
│   ├── main.py              # App entry point & lifespan setup
│   ├── config.py            # Pydantic settings from .env
│   ├── models.py            # Request/Response schemas & Enums
│   ├── seed_kb.py           # Populates & warms Moss knowledge base
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Backend environment template
│   └── services/
│       ├── llm_service.py       # LLM claim extraction & verdict wrapper
│       ├── retrieval_service.py # Moss sub-10ms retrieval wrapper
│       └── pipeline.py         # End-to-end async validation pipeline
│
├── frontend/                # Next.js 15 React & TypeScript dashboard
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # Dashboard interactive UI
│   │   │   ├── layout.tsx       # Root layout & meta tags
│   │   │   └── globals.css      # Design system & visual styles
│   │   ├── components/
│   │   │   ├── LatencyBar.tsx   # Pipeline visual timing breakdown
│   │   │   ├── ClaimCard.tsx    # Fact-check result card with matched context
│   │   │   └── StatusBadge.tsx  # Overall SAFE/UNSAFE glow badge
│   │   ├── lib/
│   │   │   └── api.ts           # Async API fetch client
│   │   └── types/
│   │       └── index.ts         # Shared TypeScript interfaces
│   ├── .env.example         # Frontend environment template
│   └── package.json
│
└── README.md
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** and npm
- **Moss Credentials**: Project ID & API Key from [moss.dev](https://moss.dev)
- **OpenAI API Key**: From [platform.openai.com](https://platform.openai.com)

---

### 1. Backend Setup

```bash
cd backend

# Create & activate virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS / Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Fill in MOSS_PROJECT_ID, MOSS_PROJECT_KEY, and OPENAI_API_KEY in .env

# Seed & warm the Moss knowledge base
python seed_kb.py

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

The backend server will run at **`http://localhost:8000`**.

---

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Next.js dev server
npm run dev
```

The frontend dashboard will run at **`http://localhost:3000`**.

---

## 🎯 Demo & "Caught It" Sample Test

Open **`http://localhost:3000`**, click **📋 Load Sample** (or paste the text below), and click **⚡ Run Guardrail Check**:

> CloudVault is a great platform for teams of all sizes. It offers end-to-end encryption on all plans to keep your data completely secure. The Pro plan costs $29 per month and includes priority support with a 4-hour response SLA. Free tier users get 24/7 email support for any issues they encounter. They guarantee 99.99% uptime across all paid plans, and the platform is fully HIPAA compliant for healthcare data.

### Expected Results:
- 🟢 **Grounded**: *"The Pro plan costs $29 per month..."* (Matches CloudVault KB document)
- 🔴 **Contradicted**: *"offers end-to-end encryption"* (KB explicitly states CloudVault does NOT offer E2E encryption)
- 🔴 **Contradicted**: *"Free tier users get 24/7 email support"* (KB states Free tier has community support only)
- 🔴 **Contradicted**: *"guarantee 99.99% uptime"* (KB states 99.9% uptime SLA, explicitly NOT 99.99%)
- 🔴 **Contradicted**: *"fully HIPAA compliant"* (KB states CloudVault is NOT HIPAA compliant)

---

## 🔌 API Reference

### `POST /v1/validate`
Validate an AI agent's response against the Moss knowledge base.

**Request Body:**
```json
{
  "text": "The AI agent response string to validate..."
}
```

**Response Body:**
```json
{
  "claims": [
    {
      "claim": "CloudVault offers end-to-end encryption on all plans.",
      "verdict": "contradicted",
      "confidence": 0.98,
      "reason": "Knowledge base explicitly states CloudVault does NOT offer end-to-end encryption.",
      "matched_context": [
        "CloudVault encrypts all data at rest using AES-256 encryption. CloudVault does NOT offer end-to-end encryption."
      ],
      "retrieval_latency_ms": 2.3,
      "verdict_latency_ms": 142.1
    }
  ],
  "latency_breakdown": {
    "extraction_ms": 185.2,
    "total_retrieval_ms": 4.8,
    "total_verdict_ms": 410.5,
    "total_ms": 605.5
  },
  "overall_status": "unsafe"
}
```

### `GET /health`
Returns system health status: `{"status": "ok", "service": "mossguard"}`.

---

## 🛠️ Environment Variables Reference

| Variable | Service | Description | Default |
|---|---|---|---|
| `MOSS_PROJECT_ID` | Backend | Moss Project ID from moss.dev | *Required* |
| `MOSS_PROJECT_KEY` | Backend | Moss Project API Key | *Required* |
| `MOSS_INDEX_NAME` | Backend | Moss index identifier | `mossguard-kb` |
| `OPENAI_API_KEY` | Backend | OpenAI API Key for claim extraction & classification | *Required* |
| `LLM_MODEL` | Backend | OpenAI model name | `gpt-4o-mini` |
| `NEXT_PUBLIC_API_URL` | Frontend | Backend URL endpoint | `http://localhost:8000` |

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
