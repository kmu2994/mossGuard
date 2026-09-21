/**
 * TypeScript interfaces matching the MossGuard backend API response schema.
 */

export type Verdict = "grounded" | "contradicted" | "unsupported";
export type OverallStatus = "safe" | "unsafe";
export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface ClaimResult {
  claim: string;
  verdict: Verdict;
  confidence: number;
  reason: string;
  matched_context: string[];
  retrieval_latency_ms: number;
  verdict_latency_ms: number;
}

export interface LatencyBreakdown {
  extraction_ms: number;
  total_retrieval_ms: number;
  total_verdict_ms: number;
  total_ms: number;
}

export interface ClaimSummary {
  grounded: number;
  contradicted: number;
  unsupported: number;
}

export interface ValidateResponse {
  claims: ClaimResult[];
  latency_breakdown: LatencyBreakdown;
  overall_status: OverallStatus;
  trust_score: number;
  risk_level: RiskLevel;
  claim_summary: ClaimSummary;
}

export interface ValidateRequest {
  text: string;
}
