/**
 * ClaimCard — Displays a single claim with verdict, confidence, and context.
 * Color-coded by verdict: green=grounded, red=contradicted, orange=unsupported.
 */

import type { ClaimResult } from "@/types";
import styles from "./ClaimCard.module.css";

interface ClaimCardProps {
  claim: ClaimResult;
  index: number;
}

const VERDICT_CONFIG = {
  grounded: {
    label: "Grounded",
    icon: "✓",
    className: "grounded",
  },
  contradicted: {
    label: "Contradicted",
    icon: "✗",
    className: "contradicted",
  },
  unsupported: {
    label: "Unsupported",
    icon: "?",
    className: "unsupported",
  },
} as const;

export default function ClaimCard({ claim, index }: ClaimCardProps) {
  const config = VERDICT_CONFIG[claim.verdict];
  const totalClaimMs = claim.retrieval_latency_ms + claim.verdict_latency_ms;

  return (
    <div
      className={`${styles.card} ${styles[config.className]}`}
      style={{ animationDelay: `${index * 0.08}s` }}
    >
      <div className={styles.header}>
        <span className={`${styles.badge} ${styles[`badge_${config.className}`]}`}>
          <span className={styles.badgeIcon}>{config.icon}</span>
          {config.label}
        </span>
        <div className={styles.timings}>
          <span className={styles.timing} title="Moss retrieval time">
            🔍 {claim.retrieval_latency_ms.toFixed(1)}ms
          </span>
          <span className={styles.timing} title="Verdict classification time">
            ⚖️ {claim.verdict_latency_ms.toFixed(1)}ms
          </span>
          <span className={styles.timingTotal} title="Total for this claim">
            Σ {totalClaimMs.toFixed(1)}ms
          </span>
        </div>
      </div>

      <p className={styles.claimText}>&ldquo;{claim.claim}&rdquo;</p>

      <div className={styles.meta}>
        <div className={styles.confidenceBar}>
          <span className={styles.confidenceLabel}>Confidence</span>
          <div className={styles.confidenceTrack}>
            <div
              className={`${styles.confidenceFill} ${styles[`fill_${config.className}`]}`}
              style={{ width: `${claim.confidence * 100}%` }}
            />
          </div>
          <span className={styles.confidenceValue}>
            {(claim.confidence * 100).toFixed(0)}%
          </span>
        </div>
        <p className={styles.reason}>{claim.reason}</p>
      </div>

      {claim.matched_context.length > 0 && (
        <details className={styles.contextSection}>
          <summary className={styles.contextToggle}>
            📄 Matched Context ({claim.matched_context.length})
          </summary>
          <ul className={styles.contextList}>
            {claim.matched_context.map((ctx, i) => (
              <li key={i} className={styles.contextItem}>
                {ctx}
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
