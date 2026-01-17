// Interaction detection module for Polymarket
// Detects hover on market cards/outcome rows and trade module opening

export interface DetectedInteraction {
  marketUrl: string;
  side?: 'YES' | 'NO';
  amount?: number;
  triggerType: 'hover' | 'ticket_open';
}

// Heuristics to identify market cards and outcome rows
const MARKET_CARD_SELECTORS = [
  'a[href*="/event/"]',
  '[data-testid*="market"]',
  '[data-testid*="event"]',
  '[class*="market-card"]',
  '[class*="event-card"]',
];

const TRADE_MODULE_SELECTORS = [
  '[class*="trade-ticket"]',
  '[class*="trade-panel"]',
  '[class*="order-ticket"]',
  '[data-testid*="trade"]',
  '[data-testid*="order"]',
];

const HOVER_DEBOUNCE_MS = 250;
const RATE_LIMIT_MS = 1000; // Max 1 call per second

let hoverTimeout: number | null = null;
let lastCallTime = 0;
let currentHoverTarget: HTMLElement | null = null;

function extractMarketUrl(element: HTMLElement): string | null {
  // Try to find a link to /event/...
  const link = element.closest('a[href*="/event/"]') as HTMLAnchorElement;
  if (link?.href) {
    return link.href;
  }
  
  // Try to find href in element itself
  if (element instanceof HTMLAnchorElement && element.href) {
    return element.href;
  }
  
  // Try parent elements
  let parent = element.parentElement;
  for (let i = 0; i < 5 && parent; i++) {
    if (parent instanceof HTMLAnchorElement && parent.href?.includes('/event/')) {
      return parent.href;
    }
    parent = parent.parentElement;
  }
  
  // Fallback: use current page URL if on a market page
  if (window.location.href.includes('/event/')) {
    return window.location.href;
  }
  
  return null;
}

function detectSideFromElement(element: HTMLElement): 'YES' | 'NO' | undefined {
  const text = element.textContent?.toLowerCase() || '';
  const ariaLabel = element.getAttribute('aria-label')?.toLowerCase() || '';
  const combined = `${text} ${ariaLabel}`;
  
  // Check for YES/NO indicators
  if (combined.includes('yes') || combined.includes('buy')) {
    return 'YES';
  }
  if (combined.includes('no') || combined.includes('sell')) {
    return 'NO';
  }
  
  // Check for selected toggle/button
  const selectedToggle = element.closest('[class*="selected"], [aria-selected="true"]');
  if (selectedToggle) {
    const toggleText = selectedToggle.textContent?.toLowerCase() || '';
    if (toggleText.includes('yes')) return 'YES';
    if (toggleText.includes('no')) return 'NO';
  }
  
  return undefined;
}

function detectAmountFromElement(element: HTMLElement): number | undefined {
  // Look for amount input
  const amountInput = element.querySelector('input[type="number"], input[placeholder*="$"], input[placeholder*="amount"]') as HTMLInputElement;
  if (amountInput?.value) {
    const value = parseFloat(amountInput.value.replace(/,/g, ''));
    if (!isNaN(value)) return value;
  }
  
  // Look for amount in nearby text
  const parent = element.closest('[class*="trade"], [class*="order"], [class*="market"]');
  if (parent) {
    const amountText = parent.textContent?.match(/\$?([\d,]+\.?\d*)/);
    if (amountText) {
      const value = parseFloat(amountText[1].replace(/,/g, ''));
      if (!isNaN(value)) return value;
    }
  }
  
  return undefined;
}

function isMarketCardOrOutcomeRow(element: HTMLElement): boolean {
  // Check if element or parent matches market card patterns
  for (const selector of MARKET_CARD_SELECTORS) {
    if (element.matches(selector) || element.closest(selector)) {
      return true;
    }
  }
  
  // Check for link to /event/
  if (extractMarketUrl(element)) {
    return true;
  }
  
  return false;
}

function isTradeModuleVisible(): boolean {
  for (const selector of TRADE_MODULE_SELECTORS) {
    const element = document.querySelector(selector);
    if (element) {
      const style = window.getComputedStyle(element);
      if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
        return true;
      }
    }
  }
  return false;
}

export function setupInteractionDetection(
  onInteractionDetected: (interaction: DetectedInteraction) => void
): () => void {
  let observer: MutationObserver | null = null;
  let tradeModuleObserver: MutationObserver | null = null;
  let tradeModuleVisible = false;
  
  function handleHover(event: PointerEvent) {
    const target = event.target as HTMLElement;
    if (!target) return;
    
    // Check if hovering a market card or outcome row
    if (!isMarketCardOrOutcomeRow(target)) {
      return;
    }
    
    const marketUrl = extractMarketUrl(target);
    if (!marketUrl) return;
    
    currentHoverTarget = target;
    
    // Clear existing timeout
    if (hoverTimeout !== null) {
      clearTimeout(hoverTimeout);
    }
    
    // Debounce: wait 250ms before triggering
    hoverTimeout = window.setTimeout(() => {
      // Check rate limit
      const now = Date.now();
      if (now - lastCallTime < RATE_LIMIT_MS) {
        return; // Rate limited
      }
      
      const side = detectSideFromElement(target);
      const amount = detectAmountFromElement(target);
      
      onInteractionDetected({
        marketUrl,
        side,
        amount,
        triggerType: 'hover',
      });
      
      lastCallTime = now;
    }, HOVER_DEBOUNCE_MS);
  }
  
  function handleHoverEnd() {
    if (hoverTimeout !== null) {
      clearTimeout(hoverTimeout);
      hoverTimeout = null;
    }
    currentHoverTarget = null;
  }
  
  function checkTradeModule() {
    const isVisible = isTradeModuleVisible();
    
    if (isVisible && !tradeModuleVisible) {
      // Trade module just opened
      tradeModuleVisible = true;
      
      // Check rate limit
      const now = Date.now();
      if (now - lastCallTime < RATE_LIMIT_MS) {
        return; // Rate limited
      }
      
      const marketUrl = window.location.href;
      if (marketUrl.includes('/event/')) {
        // Try to detect side from trade module
        const tradeModule = document.querySelector(TRADE_MODULE_SELECTORS[0]);
        const side = tradeModule ? detectSideFromElement(tradeModule as HTMLElement) : undefined;
        const amount = tradeModule ? detectAmountFromElement(tradeModule as HTMLElement) : undefined;
        
        onInteractionDetected({
          marketUrl,
          side,
          amount,
          triggerType: 'ticket_open',
        });
        
        lastCallTime = now;
      }
    } else if (!isVisible && tradeModuleVisible) {
      tradeModuleVisible = false;
    }
  }
  
  function setupListeners() {
    // Document-level pointer events for hover detection
    document.addEventListener('pointerenter', handleHover, true);
    document.addEventListener('pointerleave', handleHoverEnd, true);
    
    // Watch for trade module visibility
    checkTradeModule();
    
    // Set up observer for trade module
    if (!tradeModuleObserver) {
      tradeModuleObserver = new MutationObserver(() => {
        checkTradeModule();
      });
      
      tradeModuleObserver.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class', 'style', 'data-testid'],
      });
    }
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
    setTimeout(() => {
      tradeModuleVisible = false;
      setupListeners();
    }, 100);
  };
  
  history.replaceState = function(...args) {
    originalReplaceState.apply(history, args);
    setTimeout(() => {
      tradeModuleVisible = false;
      setupListeners();
    }, 100);
  };
  
  window.addEventListener('popstate', () => {
    setTimeout(() => {
      tradeModuleVisible = false;
      setupListeners();
    }, 100);
  });
  
  // Cleanup function
  return () => {
    if (hoverTimeout !== null) {
      clearTimeout(hoverTimeout);
    }
    if (observer) {
      observer.disconnect();
    }
    if (tradeModuleObserver) {
      tradeModuleObserver.disconnect();
    }
    document.removeEventListener('pointerenter', handleHover, true);
    document.removeEventListener('pointerleave', handleHoverEnd, true);
    history.pushState = originalPushState;
    history.replaceState = originalReplaceState;
  };
}
