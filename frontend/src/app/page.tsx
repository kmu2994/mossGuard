"use client";

import { useState } from "react";
import type { ValidateResponse } from "@/types";
import { validate } from "@/lib/api";
import LatencyBar from "@/components/LatencyBar";
import ClaimCard from "@/components/ClaimCard";
import StatusBadge from "@/components/StatusBadge";
import LiveKitVoiceGuardrail from "@/components/LiveKitVoiceGuardrail";
import SecurityBadge from "@/components/SecurityBadge";

const SAMPLE_TEXT = `CloudVault is a great platform for teams of all sizes. It offers end-to-end encryption on all plans to keep your data completely secure. The Pro plan costs $29 per month and includes priority support with a 4-hour response SLA. Free tier users get 24/7 email support for any issues they encounter. They guarantee 99.99% uptime across all paid plans, and the platform is fully HIPAA compliant for healthcare data.`;

export default function Home() {
  const [activeTab, setActiveTab] = useState<"text" | "voice">("text");
  const [text, setText] = useState("");
  const [result, setResult] = useState<ValidateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleValidate = async () => {
    if (!text.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await validate(text);
      setResult(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unexpected error occurred."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSample = () => {
    setText(SAMPLE_TEXT);
    setResult(null);
    setError(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleValidate();
    }
  };

  const getRiskClass = (level: string) => {
    switch (level) {
      case "low": return "riskLow";
      case "medium": return "riskMedium";
      case "high": return "riskHigh";
      case "critical": return "riskCritical";
      default: return "riskLow";
    }
  };

  return (
    <>
      {/* ── Navigation Bar ───────────────────────────────────── */}
      <nav className="navbar">
        <div className="navLogo">
          <span className="navLogoIcon">🛡️</span>
          <span className="navLogoText">MossGuard</span>
        </div>
        <div className="navLinks">
          <span className="navLink">Dashboard</span>
          <span className="navLink">Docs</span>
          <span className="navLink">API</span>
          <span className="navBadge">v0.2.0</span>
        </div>
      </nav>

      <div className="pageWrapper">
        {/* ── Hero Section ──────────────────────────────────────── */}
        <section className="hero">
          <div className="heroContent">
            <h1 className="heroTitle">
              Catch hallucinations
              <br />
              before they reach
              <br />
              your users.
            </h1>
            <p className="heroSubtitle">
              Real-time AI agent guardrails with sub-10ms semantic retrieval
              and mandatory LiveKit WebRTC real-time voice stream evaluation.
            </p>
            <div className="heroActions">
              <button
                className="submitBtn"
                onClick={() => {
                  setActiveTab("text");
                  document.getElementById("agent-response")?.focus();
                }}
              >
                Get Started ↗
              </button>
              <button
                className="sampleBtn"
                onClick={() => {
                  setActiveTab("voice");
                }}
              >
                🎙️ LiveKit Voice Guardrails
              </button>
            </div>
          </div>

          <div className="heroCard">
            <div style={{ fontSize: "0.78rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "12px" }}>
              Live Pipeline Preview
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--verdict-grounded)", flexShrink: 0 }} />
                <span style={{ fontSize: "0.88rem", color: "var(--text-secondary)" }}>Extract discrete factual claims</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--accent-teal-light)", flexShrink: 0 }} />
                <span style={{ fontSize: "0.88rem", color: "var(--text-secondary)" }}>Moss retrieval in &lt;10ms</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "var(--accent-coral)", flexShrink: 0 }} />
                <span style={{ fontSize: "0.88rem", color: "var(--text-secondary)" }}>LiveKit WebRTC voice stream evaluation</span>
              </div>
            </div>
            <div style={{ marginTop: "20px", padding: "14px 16px", background: "var(--bg-primary)", borderRadius: "10px", border: "1px solid var(--border)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>Avg. retrieval latency</span>
                <span style={{ fontSize: "1.4rem", fontWeight: 800, color: "var(--accent-teal)" }}>1.8<span style={{ fontSize: "0.78rem", fontWeight: 500, color: "var(--text-muted)" }}>ms</span></span>
              </div>
            </div>
          </div>
        </section>

        {/* ── Enterprise Security Audit Section ──────────────────── */}
        <SecurityBadge />

        {/* ── Mode Switcher Tabs ───────────────────────────────── */}
        <div style={{ display: "flex", gap: "12px", marginBottom: "24px" }}>
          <button
            onClick={() => setActiveTab("text")}
            style={{
              padding: "10px 22px",
              borderRadius: "10px",
              border: "1px solid var(--border)",
              background: activeTab === "text" ? "var(--accent-teal)" : "var(--card-bg)",
              color: activeTab === "text" ? "#ffffff" : "var(--text-secondary)",
              fontWeight: 600,
              fontSize: "0.92rem",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
          >
            ⚡ Text Guardrail Check
          </button>
          <button
            onClick={() => setActiveTab("voice")}
            style={{
              padding: "10px 22px",
              borderRadius: "10px",
              border: "1px solid var(--border)",
              background: activeTab === "voice" ? "var(--accent-teal)" : "var(--card-bg)",
              color: activeTab === "voice" ? "#ffffff" : "var(--text-secondary)",
              fontWeight: 600,
              fontSize: "0.92rem",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
          >
            🎙️ LiveKit Voice Guardrails
          </button>
        </div>

        {/* ── LiveKit Voice Guardrail View ─────────────────────── */}
        {activeTab === "voice" && <LiveKitVoiceGuardrail />}

        {/* ── Text Guardrail View ──────────────────────────────── */}
        {activeTab === "text" && (
          <>
            <section className="inputSection" id="input-section">
              <div className="inputHeader">
                <label htmlFor="agent-response" className="inputLabel">
                  AI Agent Response
                </label>
                <span className="inputHint">Ctrl+Enter to validate</span>
              </div>
              <textarea
                id="agent-response"
                className="textarea"
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Paste an AI agent's response here to fact-check it against the knowledge base..."
                disabled={loading}
              />
              <div className="buttonRow">
                <button
                  id="validate-btn"
                  className="submitBtn"
                  onClick={handleValidate}
                  disabled={loading || !text.trim()}
                >
                  {loading ? (
                    <>
                      <span className="spinner" />
                      Validating…
                    </>
                  ) : (
                    <>Run Guardrail Check ↗</>
                  )}
                </button>
                <button
                  id="sample-btn"
                  className="sampleBtn"
                  onClick={handleLoadSample}
                  disabled={loading}
                >
                  📋 Load Sample
                </button>
              </div>
            </section>

            {/* Error */}
            {error && (
              <div className="error" role="alert">
                <strong>Error:</strong> {error}
              </div>
            )}

            {/* Results */}
            {result && (
              <section className="results">
                <div className="statusRow">
                  <StatusBadge
                    status={result.overall_status}
                    claimCount={result.claims.length}
                  />
                </div>

                {result.claim_summary && (
                  <div className="summaryRow">
                    <div className="summaryCard">
                      <div className="summaryValue trustScoreValue">
                        {result.trust_score?.toFixed(0) ?? "—"}
                      </div>
                      <div className="summaryLabel">Trust Score</div>
                    </div>
                    <div className="summaryCard">
                      <div className={`summaryValue ${getRiskClass(result.risk_level ?? "low")}`}>
                        {result.risk_level?.toUpperCase() ?? "—"}
                      </div>
                      <div className="summaryLabel">Risk Level</div>
                    </div>
                    <div className="summaryCard">
                      <div className="summaryValue groundedValue">
                        {result.claim_summary.grounded}
                      </div>
                      <div className="summaryLabel">Grounded</div>
                    </div>
                    <div className="summaryCard">
                      <div className="summaryValue contradictedValue">
                        {result.claim_summary.contradicted}
                      </div>
                      <div className="summaryLabel">Contradicted</div>
                    </div>
                    <div className="summaryCard">
                      <div className="summaryValue unsupportedValue">
                        {result.claim_summary.unsupported}
                      </div>
                      <div className="summaryLabel">Unsupported</div>
                    </div>
                  </div>
                )}

                <LatencyBar breakdown={result.latency_breakdown} />

                <div className="claimsList">
                  {result.claims.map((claim, i) => (
                    <ClaimCard key={i} claim={claim} index={i} />
                  ))}
                </div>
              </section>
            )}

            {/* Empty state */}
            {!result && !error && !loading && (
              <div className="emptyState">
                <div className="emptyIcon">🔍</div>
                <p className="emptyTitle">Ready to validate</p>
                <p className="emptyText">
                  Paste an AI agent&apos;s response above and click{" "}
                  <strong>Run Guardrail Check</strong> to validate its claims
                  against the knowledge base.
                </p>
              </div>
            )}
          </>
        )}

        {/* ── Footer ──────────────────────────────────────────── */}
        <footer className="footer">
          <div className="footerBrands">
            <span className="footerBrand">LiveKit WebRTC</span>
            <span className="footerBrand">Moss Sub-10ms</span>
            <span className="footerBrand">OAuth2 / JWT</span>
            <span className="footerBrand">FastAPI</span>
            <span className="footerBrand">Next.js 15</span>
          </div>
          <p className="footerText">
            MossGuard — Real-time AI agent trust &amp; voice guardrail system
          </p>
        </footer>
      </div>
    </>
  );
}
