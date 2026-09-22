# 🎬 MossGuard — 2-Minute Hackathon Demo Video Script & Walkthrough Guide

Use this standalone guide while screen recording your project demo video for hackathon submission.

---

## 🛠️ Recording Setup Checklist
- [ ] Open the web app in your browser: `http://localhost:3000` (or your live Vercel deployment URL).
- [ ] Ensure microphone audio is clear and browser is set to 100% zoom (1080p full screen).
- [ ] Keep the **Load Sample** button ready in case you want to load the text with one click.
- [ ] Estimated Video Duration: **2 Minutes 15 Seconds**.

---

## ⏱️ Step-by-Step Script & Video Guide

### 📍 Scene 1: Introduction & Problem Statement (0:00 – 0:25)

**🎥 Screen Focus**: Top of the MossGuard dashboard showing the hero title *"Catch hallucinations before they reach your users"*, navigation bar, and key feature badges.

**🗣️ Spoken Script**:
> *"Hello judges! Welcome to **MossGuard**, a real-time AI agent trust and guardrail system designed to catch hallucinations before they ever reach your users.*
>
> *As AI agents are deployed in customer support, financial services, and healthcare, hallucinations pose a massive liability. Traditional guardrail systems rely on heavy remote vector databases that add 150 to 400 milliseconds per retrieval call. When evaluating multiple claims, that latency quickly exceeds a full second, breaking real-time user experience.*
>
> ***MossGuard solves this by leveraging Moss's sub-10ms in-memory semantic retrieval engine.***"

---

### 📍 Scene 2: Live Demo — Running a Guardrail Check (0:25 – 0:55)

**🎥 Screen Focus**: Scroll down slightly to the text area input section. Click **📋 Load Sample** to populate the input box, then click **⚡ Run Guardrail Check**.

**🗣️ Spoken Script**:
> *"Let's test MossGuard live with an AI agent response about a fictional SaaS platform called CloudVault.*
>
> *Notice that this agent's response contains several plausible statements regarding pricing, storage limits, SLA guarantees, encryption, and support options.*
>
> *I'll click **Run Guardrail Check**. MossGuard immediately executes a multi-stage validation pipeline: first isolating discrete factual claims with Gemini, querying our Moss knowledge base concurrently in parallel, and evaluating each claim against trusted source passages."*

---

### 📍 Scene 3: Highlighting Caught Hallucinations & Guardrail Metrics (0:55 – 1:35)

**🎥 Screen Focus**: Highlight the **Status Badge** (`UNSAFE`), **Trust Score** (36%), **Risk Level** (`HIGH`), and point out the color-coded **Claim Cards**. Expand the **Matched Context** dropdown on a red contradicted card.

**🗣️ Spoken Script**:
> *"Look at the results! MossGuard flagged the overall response as **UNSAFE** with a **Trust Score of 36%** and **HIGH Risk Level**.*
>
> *Let's check the claim breakdown:*
> - *🟢 **Grounded Claim**: 'The Pro plan costs $29 per month...' — Verified by our CloudVault pricing documentation.*
> - *🔴 **Contradicted Hallucination**: 'Offers end-to-end encryption...' — MossGuard caught this! The knowledge base explicitly states CloudVault does NOT offer E2E encryption.*
> - *🔴 **Contradicted Hallucination**: 'Fully HIPAA compliant...' — Caught! Our security document explicitly warns that CloudVault is NOT HIPAA compliant.*
> - *🔴 **Contradicted Hallucination**: 'Free tier gets 24/7 email support...' — Refuted by our support SLA doc.*
>
> *We can expand the **Matched Context** on any claim card to inspect the exact source passages retrieved from Moss."*

---

### 📍 Scene 4: The Moss Sub-10ms Differentiator & Latency Breakdown (1:35 – 2:05)

**🎥 Screen Focus**: Focus on the **Pipeline Latency Bar** showing the stage breakdown (Extraction, Moss Retrieval, Verdict).

**🗣️ Spoken Script**:
> *"Now let's look at what makes MossGuard uniquely viable for production: **The Pipeline Latency Breakdown**.*
>
> *While LLM claim extraction and verdict classification take standard time, look at **Moss Retrieval latency**: **under 2 milliseconds** for semantic vector search!*
>
> *Because Moss loads indexes directly into local process memory, queries bypass external network roundtrips entirely. This enables MossGuard to validate multiple claims concurrently without inflating latency."*

---

### 📍 Scene 5: Conclusion & Wrap-Up (2:05 – 2:15)

**🎥 Screen Focus**: Scroll up to show the full dashboard, modern light UI, navigation bar, and footer tech badges (Moss, FastAPI, Next.js, Gemini).

**🗣️ Spoken Script**:
> *"In summary, MossGuard delivers robust hallucination prevention with sub-10ms retrieval, automated claim extraction, trust scoring, and a classic responsive dashboard built with Next.js and FastAPI.*
>
> *Thank you for watching!"*

---

## 📋 Quick Readout Sheet (Cheat Sheet)

If you prefer reading bullet points while recording:
1. **Pitch**: Guardrail system catching LLM hallucinations using Moss sub-10ms retrieval.
2. **Problem**: Traditional vector DBs add 150-400ms per retrieval, breaking real-time guardrails.
3. **Demo**: Load sample text, run check -> catches E2E encryption & HIPAA compliance hallucinations.
4. **Metrics**: Status (UNSAFE), Trust Score (36%), Risk Level (HIGH), Color-coded claim cards.
5. **Differentiator**: Moss retrieval in <2ms via local in-memory index.
