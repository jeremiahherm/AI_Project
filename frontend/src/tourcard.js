function getScoreLabel(score) {
  if (score >= 4) return { text: 'Very Positive', key: 'vp' };
  if (score >= 3) return { text: 'Positive', key: 'p'  };
  if (score >= 2) return { text: 'Neutral', key: 'n'  };
  if (score >= 1) return { text: 'Negative', key: 'neg'};
  return { text: 'Very Negative', key: 'vn' };
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
  return `
    <div style="display:flex;flex-direction:column;gap:12px;max-width:92%;">
      <div style="font-size:18px;color:white;">
        Based on your trip to ${escapeHtml(tour.destination)} from ${escapeHtml(tour.start_date)} to ${escapeHtml(tour.end_date)}, here are some tour options I found:
      </div>
      ${tour.reviews.sort((a, b) => b.score - a.score).map(formatReviewCard).join('')}
    </div>
  `;
}

function formatReviewCard(review) {
  const score = getScoreLabel(review.score);
  return `
    <div class="tour-card">
      <div class="tc-header">
        <div class="tc-name">${escapeHtml(review.tour_name)}</div>
        <div class="tc-price">$${escapeHtml(String((Math.round(review.price * 100) / 100).toFixed(2)))} <div class="tc-pp"> per person</div></div>
      </div>
      <div class="tc-meta">
        <span class="tc-company">${escapeHtml(review.company_name)}</span>
        <span class="score-pill score-${score.key}">${score.text}</span>
      </div>
      <div class="tc-body">${escapeHtml(review.reasoning)}</div>
      <div class="tc-footer">
        <a class="tc-link" href="${escapeHtml(review.viator_link)}" target="_blank">
          View on Viator <span style="font-size:11px">↗</span>
        </a>
      </div>
    </div>
  `;
}

