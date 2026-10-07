// AI Fact Checker - Content Script

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "showLoading") {
    showOverlay(`
      <div class="factcheck-card factcheck-loading">
        <div class="factcheck-spinner"></div>
        <div class="factcheck-text">Fact-checking claim: "<em>${escapeHtml(request.text)}</em>"...</div>
      </div>
    `);
  } else if (request.action === "showResult") {
    const data = request.data;
    const claimObj = (data.claims && data.claims.length > 0) ? data.claims[0] : data;
    const verdict = claimObj.verdict || "UNVERIFIED";
    const confidenceStr = claimObj.confidence ? `${claimObj.confidence} Confidence` : "";
    const summary = claimObj.reasoning || claimObj.summary || "No detailed summary provided.";

    const verdictClass = verdict.toUpperCase() === "TRUE" ? "true" 
      : verdict.toUpperCase() === "FALSE" ? "false" 
      : "mixed";

    showOverlay(`
      <div class="factcheck-card factcheck-result">
        <div class="factcheck-header">
          <span class="factcheck-badge factcheck-badge-${verdictClass}">${escapeHtml(verdict)}</span>
          <span class="factcheck-confidence">${escapeHtml(confidenceStr)}</span>
          <button class="factcheck-close">&times;</button>
        </div>
        <div class="factcheck-body">
          <p class="factcheck-summary">${escapeHtml(summary)}</p>
        </div>
      </div>
    `);
  } else if (request.action === "showError") {
    showOverlay(`
      <div class="factcheck-card factcheck-error">
        <div class="factcheck-header">
          <span class="factcheck-badge factcheck-badge-error">Error</span>
          <button class="factcheck-close">&times;</button>
        </div>
        <div class="factcheck-body">
          <p>${escapeHtml(request.error || "Failed to reach backend server.")}</p>
        </div>
      </div>
    `);
  }
});

function showOverlay(htmlContent) {
  removeOverlay();
  const overlay = document.createElement("div");
  overlay.id = "factcheck-extension-overlay";
  overlay.innerHTML = htmlContent;

  const closeBtn = overlay.querySelector(".factcheck-close");
  if (closeBtn) {
    closeBtn.addEventListener("click", removeOverlay);
  }

  document.body.appendChild(overlay);
}

function removeOverlay() {
  const existing = document.getElementById("factcheck-extension-overlay");
  if (existing) {
    existing.remove();
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/[&<>"']/g, (m) => {
    return {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    }[m];
  });
}
