// Background service worker (MVP - minimal with proper message handling)

console.debug('[BG] Background script loaded');

chrome.runtime.onInstalled.addListener(() => {
  console.debug('[BG] Polymarket Trade Assistant installed');
});

// Message handler - properly handle async responses
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.debug('[BG] Received message:', request);

  // Always return true to indicate we'll respond asynchronously
  (async () => {
    try {
      switch (request.type) {
        case 'PING':
          console.debug('[BG] PING received, responding PONG');
          sendResponse({ ok: true, data: 'PONG' });
          break;

        default:
          console.debug('[BG] Unknown message type:', request.type);
          sendResponse({ ok: false, error: 'Unknown message type' });
      }
    } catch (error) {
      console.error('[BG] Error handling message:', error);
      sendResponse({ ok: false, error: String(error) });
    }
  })();

  // Return true to indicate we'll respond asynchronously
  return true;
});

// Handle openUrl messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'openUrl') {
    try {
      const url = request.url;
      // Validate URL format
      if (!url || typeof url !== 'string') {
        sendResponse({ success: false, error: 'Invalid URL' });
        return true;
      }

      // Only allow http(s) and common protocols
      if (!url.match(/^https?:\/\//)) {
        sendResponse({ success: false, error: 'Unsupported protocol' });
        return true;
      }

      // Open URL in new tab
      chrome.tabs.create({ url, active: false });
      console.debug('[BG] Opened URL:', url);
      sendResponse({ success: true });
    } catch (error) {
      console.error('[BG] Error opening URL:', error);
      sendResponse({ success: false, error: String(error) });
    }
    return true;
  }
});

