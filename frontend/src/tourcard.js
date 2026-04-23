function getScoreLabel(score) {
  const labels = {
    0: { text: 'Very Negative', color: '#ef4444' },
    1: { text: 'Negative',      color: '#f97316' },
    2: { text: 'Neutral',       color: '#eab308' },
    3: { text: 'Positive',      color: '#22c55e' },
    4: { text: 'Very Positive', color: '#16a34a' },
  };
  return labels[score] ?? { text: 'Unknown', color: '#6b7280' };
}


export function escapeHtml(str) {
  if (typeof str !== 'string') return String(str ?? '');
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/\n/g, '<br>');
}


export function formatTourCard(tour) {
  const scoreInfo = getScoreLabel(tour.score);
  const locationList = (tour.locations ?? [])
    .map(loc => `<li>📍 ${escapeHtml(loc.name ?? loc)}</li>`)
    .join('');

  return `
    <div class="tour-card">
      <div class="tour-header">
        <span class="tour-name">${escapeHtml(tour.tour_name)}</span>
        <span class="tour-price">$${tour.price}</span>
      </div>

      <div class="tour-score" style="color: ${scoreInfo.color};">
        ● Crowd Sentiment: <strong>${escapeHtml(scoreInfo.text)}</strong>
      </div>

      ${locationList ? `
        <ul class="tour-locations">${locationList}</ul>
      ` : ''}

      <a class="tour-link" href="${escapeHtml(tour.viator_link)}" target="_blank" rel="noopener">
        View on Viator →
      </a>
    </div>
  `;
}
