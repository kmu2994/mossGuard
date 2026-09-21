/**
 * StatusBadge — Overall status indicator (SAFE / UNSAFE) with animated glow.
 */

import type { OverallStatus } from "@/types";
import styles from "./StatusBadge.module.css";

interface StatusBadgeProps {
  status: OverallStatus;
  claimCount: number;
}

export default function StatusBadge({ status, claimCount }: StatusBadgeProps) {
  const isSafe = status === "safe";

  return (
    <div className={`${styles.badge} ${isSafe ? styles.safe : styles.unsafe}`}>
      <div className={styles.glow} />
      <span className={styles.icon}>{isSafe ? "🛡️" : "⚠️"}</span>
      <div className={styles.content}>
        <span className={styles.label}>
          {isSafe ? "SAFE" : "UNSAFE"}
        </span>
        <span className={styles.detail}>
          {claimCount} claim{claimCount !== 1 ? "s" : ""} analysed
        </span>
      </div>
    </div>
  );
}
