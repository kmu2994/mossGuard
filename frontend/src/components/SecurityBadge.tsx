/**
 * SecurityBadge — Displays PRD Security Compliance Badges (OAuth2/JWT, Rate Limiting, AES-256, TLS 1.3, CRISPE).
 */

"use client";

import { useEffect, useState } from "react";
import type { SecurityAuditInfo } from "@/types";
import { getSecuritySpec } from "@/lib/api";
import styles from "./SecurityBadge.module.css";

export default function SecurityBadge() {
  const [spec, setSpec] = useState<SecurityAuditInfo | null>(null);

  useEffect(() => {
    getSecuritySpec().then(setSpec);
  }, []);

  if (!spec) return null;

  return (
    <div className={styles.container}>
      <div className={styles.titleGroup}>
        <span className={styles.icon}>🔒</span>
        <div>
          <h3 className={styles.title}>Enterprise Security &amp; Compliance Audit</h3>
          <p className={styles.subtitle}>
            OAuth2/JWT · AES-256 Data at Rest · TLS 1.3 in Transit · CRISPE Prompt Standard
          </p>
        </div>
      </div>

      <div className={styles.badgesRow}>
        <span className={`${styles.pill} ${styles.pillSuccess}`}>
          <span className={styles.dot} />
          OAuth2 / JWT Bearer
        </span>
        <span className={`${styles.pill} ${styles.pillSuccess}`}>
          <span className={styles.dot} />
          Rate Limit: {spec.rate_limit_per_minute}/min
        </span>
        <span className={`${styles.pill} ${styles.pillSuccess}`}>
          <span className={styles.dot} />
          {spec.encryption_at_rest} At Rest
        </span>
        <span className={`${styles.pill} ${styles.pillSuccess}`}>
          <span className={styles.dot} />
          {spec.encryption_in_transit} Transit
        </span>
        <span className={`${styles.pill} ${styles.pillSuccess}`}>
          <span className={styles.dot} />
          CRISPE Prompts
        </span>
      </div>
    </div>
  );
}
