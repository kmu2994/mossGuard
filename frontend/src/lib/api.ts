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

/**
 * Generate a signed LiveKit WebRTC access token for real-time voice stream room sessions.
 */
export async function getLiveKitToken(
  roomName: string = "mossguard-voice-room",
  identity: string = "user-agent-01"
) {
  const res = await fetch(`${API_BASE_URL}/v1/livekit/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ room_name: roomName, identity }),
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch LiveKit token: ${res.statusText}`);
  }
  return await res.json();
}

/**
 * Process a real-time transcribed audio stream chunk from a LiveKit WebRTC session.
 */
export async function processLiveKitAudioStream(
  transcript: string,
  roomName: string = "mossguard-voice-room",
  speakerId: string = "agent-speaker"
) {
  const res = await fetch(`${API_BASE_URL}/v1/livekit/process-audio-stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      transcript,
      room_name: roomName,
      speaker_id: speakerId,
    }),
  });
  if (!res.ok) {
    throw new Error(`Failed to process LiveKit stream: ${res.statusText}`);
  }
  return await res.json();
}

/**
 * Fetch explicit Security & PRD specs (OAuth2/JWT, Rate Limit, AES-256, TLS 1.3, CRISPE).
 */
export async function getSecuritySpec() {
  try {
    const res = await fetch(`${API_BASE_URL}/v1/security/spec`);
    if (res.ok) return await res.json();
  } catch {
    // Return default offline spec fallback
  }
  return {
    oauth2_jwt_enabled: true,
    rate_limiting_enabled: true,
    rate_limit_per_minute: 60,
    encryption_at_rest: "AES-256",
    encryption_in_transit: "TLS 1.3",
    prompt_engineering_standard: "CRISPE",
    opentelemetry_enabled: true,
  };
}
