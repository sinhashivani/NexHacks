// Trade detection module for Polymarket
// Detects Buy/Sell/Confirm button clicks

export interface DetectedTrade {
  side?: 'YES' | 'NO';
  amount?: number;
}

const TRADE_BUTTON_SELECTORS = [
  'button[aria-label*="Buy"]',
  'button[aria-label*="Sell"]',
  '[role="button"][aria-label*="Buy"]',
  '[role="button"][aria-label*="Sell"]',
  '[role="button"][aria-label*="Confirm"]',
];

export function detectTradeFromButton(button: HTMLElement): DetectedTrade | null {
  const text = button.textContent?.toLowerCase() || '';
  const ariaLabel = button.getAttribute('aria-label')?.toLowerCase() || '';
  const combined = `${text} ${ariaLabel}`;
  
  let side: 'YES' | 'NO' | undefined;
  let amount: number | undefined;
  
  // Detect side
  if (combined.includes('buy') || combined.includes('yes')) {
    side = 'YES';
  } else if (combined.includes('sell') || combined.includes('no')) {
    side = 'NO';
  }
  
  // Try to extract amount from nearby elements
  const parent = button.closest('[class*="trade"], [class*="order"], [class*="market"]');
  if (parent) {
    const amountText = parent.textContent?.match(/\$?([\d,]+\.?\d*)/);
    if (amountText) {
      amount = parseFloat(amountText[1].replace(/,/g, ''));
    }
  }
  
  return side ? { side, amount } : null;
}

export function setupTradeDetection(
  onTradeDetected: (trade: DetectedTrade) => void
): () => void {
  let observer: MutationObserver | null = null;
  const handledButtons = new WeakSet<HTMLElement>();
  
  function handleClick(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target || handledButtons.has(target)) return;
    
    const trade = detectTradeFromButton(target);
    if (trade) {
      handledButtons.add(target);
      onTradeDetected(trade);
    }
  }
  
  function setupListeners() {
    // Listen for clicks on potential trade buttons
    document.addEventListener('click', handleClick, true);
    
    // Also check for buttons matching selectors and text content
    for (const selector of TRADE_BUTTON_SELECTORS) {
      try {
        const buttons = document.querySelectorAll<HTMLElement>(selector);
        buttons.forEach(btn => {
          if (!handledButtons.has(btn)) {
            btn.addEventListener('click', (e) => {
              const trade = detectTradeFromButton(btn);
              if (trade) {
                handledButtons.add(btn);
                onTradeDetected(trade);
              }
            });
          }
        });
      } catch (e) {
        // Invalid selector, skip
      }
    }
    
    // Also check buttons by text content (fallback)
    const allButtons = document.querySelectorAll<HTMLElement>('button, [role="button"]');
    allButtons.forEach(btn => {
      if (!handledButtons.has(btn)) {
        const text = btn.textContent?.toLowerCase() || '';
        if (text.includes('buy') || text.includes('sell') || text.includes('confirm')) {
          btn.addEventListener('click', (e) => {
            const trade = detectTradeFromButton(btn);
            if (trade) {
              handledButtons.add(btn);
              onTradeDetected(trade);
            }
          });
        }
      }
    });
  }
  
  // Watch for DOM changes (SPA navigation)
  observer = new MutationObserver(() => {
    setupListeners();
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
  
  // Initial setup
  setupListeners();
  
  // Handle route changes
  const originalPushState = history.pushState;
  const originalReplaceState = history.replaceState;
  
  history.pushState = function(...args) {
    originalPushState.apply(history, args);
    setTimeout(setupListeners, 100);
  };
  
  history.replaceState = function(...args) {
    originalReplaceState.apply(history, args);
    setTimeout(setupListeners, 100);
  };
  
  window.addEventListener('popstate', () => {
    setTimeout(setupListeners, 100);
  });
  
  // Cleanup function
  return () => {
    if (observer) {
      observer.disconnect();
    }
    document.removeEventListener('click', handleClick, true);
    history.pushState = originalPushState;
    history.replaceState = originalReplaceState;
  };
}
