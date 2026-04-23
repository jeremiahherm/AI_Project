// ── API Config ──
const API_BASE = 'http://localhost:8000';

// ── Parse user message into TourRequest ──
// Expected format: "<destination>, <start_date> to <end_date>"
// e.g. "Paris, 2026-10-01 to 2026-10-15"
export function parseUserMessage(text) {
  const match = text.match(/^(.+?),\s*(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})$/i);
  if (!match) return null;
  return {
    destination: match[1].trim(),
    start_date: match[2],
    end_date: match[3],
  };
}

// ── GET /health ──
export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return await res.json();
}

// ── POST /tours ──
export async function fetchTourResult(tourRequest) {
  const res = await fetch(`${API_BASE}/tours`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(tourRequest),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server error: ${res.status}`);
  }

  return await res.json();
}

// ── POST /sentiment ──
export async function fetchSentiment(reviewText, rating) {
  const res = await fetch(`${API_BASE}/sentiment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ review_text: reviewText, rating }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Server error: ${res.status}`);
  }

  return await res.json();
}
