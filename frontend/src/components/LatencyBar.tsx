/**
 * LatencyBar — Prominent pipeline latency summary with visual segments.
 */

import type { LatencyBreakdown } from "@/types";
import styles from "./LatencyBar.module.css";

interface LatencyBarProps {
  breakdown: LatencyBreakdown;
}

interface Segment {
  label: string;
  value: number;
  color: string;
}

export default function LatencyBar({ breakdown }: LatencyBarProps) {
  const segments: Segment[] = [
    {
      label: "Extraction",
      value: breakdown.extraction_ms,
      color: "var(--latency-extraction)",
    },
    {
      label: "Moss Retrieval",
      value: breakdown.total_retrieval_ms,
      color: "var(--latency-retrieval)",
    },
    {
      label: "Verdict",
      value: breakdown.total_verdict_ms,
      color: "var(--latency-verdict)",
    },
  ];

  const total = breakdown.total_ms;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>⚡ Pipeline Latency</h2>
        <div className={styles.totalBadge}>
          <span className={styles.totalValue}>{total.toFixed(1)}</span>
          <span className={styles.totalUnit}>ms total</span>
        </div>
      </div>

      <div className={styles.barTrack}>
        {segments.map((seg) => {
          const widthPct = total > 0 ? (seg.value / total) * 100 : 0;
          return (
            <div
              key={seg.label}
              className={styles.barSegment}
              style={{
                width: `${Math.max(widthPct, 2)}%`,
                backgroundColor: seg.color,
              }}
              title={`${seg.label}: ${seg.value.toFixed(1)}ms`}
            />
          );
        })}
      </div>

      <div className={styles.legend}>
        {segments.map((seg) => (
          <div key={seg.label} className={styles.legendItem}>
            <span
              className={styles.legendDot}
              style={{ backgroundColor: seg.color }}
            />
            <span className={styles.legendLabel}>{seg.label}</span>
            <span className={styles.legendValue}>
              {seg.value.toFixed(1)}ms
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
