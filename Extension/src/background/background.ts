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
