/**
 * API client for communicating with the MossGuard backend.
 * Base URL is configurable via NEXT_PUBLIC_API_URL env var.
 */

import type { ValidateResponse } from "@/types";

const getApiBaseUrl = (): string => {
  if (process.env.NEXT_PUBLIC_API_URL !== undefined) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  if (
    typeof window !== "undefined" &&
    window.location.hostname !== "localhost" &&
    window.location.hostname !== "127.0.0.1"
  ) {
    return "";
  }
  return "http://127.0.0.1:8000";
};

const API_BASE_URL = getApiBaseUrl();

/**
 * Validate an AI agent's text response by running it through the
 * claim extraction → Moss retrieval → verdict pipeline.
 */
export async function validate(text: string): Promise<ValidateResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/v1/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });

    if (!res.ok) {
      let detail = "";
      try {
        const errJson = await res.json();
        detail = errJson.detail || JSON.stringify(errJson);
      } catch {
        detail = await res.text();
      }
      throw new Error(`Validation error (${res.status}): ${detail || res.statusText}`);
    }

    return await res.json();
  } catch (err) {
    if (err instanceof TypeError && err.message.toLowerCase().includes("fetch")) {
      throw new Error(
        `Unable to connect to backend server at ${API_BASE_URL}. Ensure the FastAPI server is running on port 8000.`
      );
    }
    throw err;
  }
}

/**
 * Quick health check against the backend.
 */
export async function healthCheck(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
