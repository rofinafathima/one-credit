document.addEventListener('DOMContentLoaded', () => {
  const statusEl = document.getElementById('status');
  const checkBtn = document.getElementById('checkBtn');
  const claimInput = document.getElementById('claimInput');
  const resultEl = document.getElementById('result');

  // Check API status
  fetch('http://localhost:8000/health')
    .then(res => res.json())
    .then(data => {
      statusEl.textContent = 'Online';
      statusEl.className = 'status-badge';
    })
    .catch(() => {
      statusEl.textContent = 'Offline';
      statusEl.className = 'status-badge status-offline';
    });

  checkBtn.addEventListener('click', () => {
    const claim = claimInput.value.trim();
    if (!claim) return;

    checkBtn.disabled = true;
    checkBtn.textContent = 'Checking...';
    resultEl.innerHTML = '<div class="loading"><div class="spinner"></div> Analyzing claim with AI agents...</div>';

    fetch('http://localhost:8000/api/fact-check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: claim })
    })
      .then(res => {
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        return res.json();
      })
      .then(data => {
        // The API response has: { claims: [ { claim, verdict, confidence, summary, reasoning, ... } ], status, message }
        if (data.claims && data.claims.length > 0) {
          let html = '';
          data.claims.forEach((c, i) => {
            const verdictClass = c.verdict === 'TRUE' ? 'verdict-true'
              : c.verdict === 'FALSE' ? 'verdict-false'
              : c.verdict === 'MISLEADING' ? 'verdict-misleading'
              : 'verdict-unverified';

            html += `
              <div class="claim-result">
                <div class="verdict-row">
                  <span class="verdict-badge ${verdictClass}">${c.verdict}</span>
                  <span class="confidence-label">${c.confidence} confidence</span>
                </div>
                <p class="claim-text">"${escapeHtml(c.claim)}"</p>
                <p class="reasoning">${escapeHtml(c.reasoning || c.summary)}</p>
                ${c.sources && c.sources.length > 0 ? `<p class="source-count">${c.sources.length} source(s) checked</p>` : ''}
              </div>
            `;
          });
          resultEl.innerHTML = html;
        } else {
          resultEl.innerHTML = '<div class="no-result">No claims could be analyzed.</div>';
        }
      })
      .catch(err => {
        resultEl.innerHTML = `<div class="error-msg">Error: ${escapeHtml(err.message)}</div>`;
      })
      .finally(() => {
        checkBtn.disabled = false;
        checkBtn.textContent = 'Check Claim';
      });
  });
});

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  }[m]));
}
