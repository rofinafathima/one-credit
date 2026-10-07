chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "factCheckSelection",
    title: "Fact Check: '%s'",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "factCheckSelection") {
    const text = info.selectionText;
    
    // Notify content script that we're loading
    chrome.tabs.sendMessage(tab.id, {
      action: "showLoading",
      text: text
    });

    // Make API call
    fetch("http://localhost:8000/api/fact-check", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: text })
    })
    .then(response => response.json())
    .then(data => {
      chrome.tabs.sendMessage(tab.id, {
        action: "showResult",
        data: data
      });
    })
    .catch(error => {
      console.error("Fact check error:", error);
      chrome.tabs.sendMessage(tab.id, {
        action: "showError",
        error: error.message
      });
    });
  }
});
