// Market scraping utilities (MVP - best effort)

export interface CurrentMarket {
  title: string;
  url: string;
  side?: 'YES' | 'NO';
  amount?: number;
}

export function scrapeCurrentMarket(): CurrentMarket {
  const url = window.location.href;
  
  // Try to find market title
  let title = '';
  
  // Common selectors for market titles
  const titleSelectors = [
    'h1',
    '[data-testid*="title"]',
    '[data-testid*="question"]',
    '[class*="title"]',
    '[class*="question"]',
    'h2',
  ];
  
  for (const selector of titleSelectors) {
    const element = document.querySelector(selector);
    if (element) {
      const text = element.textContent?.trim();
      if (text && text.length > 10 && text.length < 200) {
        title = text;
        break;
      }
    }
  }
  
  // Fallback: use page title
  if (!title) {
    title = document.title.replace(' | Polymarket', '').trim();
  }
  
  // Try to detect side from trade ticket
  let side: 'YES' | 'NO' | undefined;
  const tradeSelectors = [
    '[class*="trade"]',
    '[class*="order"]',
    '[data-testid*="trade"]',
  ];
  
  for (const selector of tradeSelectors) {
    const element = document.querySelector(selector);
    if (element) {
      const text = element.textContent?.toLowerCase() || '';
      if (text.includes('yes') || text.includes('buy')) {
        side = 'YES';
        break;
      }
      if (text.includes('no') || text.includes('sell')) {
        side = 'NO';
        break;
      }
    }
  }
  
  // Try to detect amount
  let amount: number | undefined;
  const amountInput = document.querySelector('input[type="number"], input[placeholder*="$"]') as HTMLInputElement;
  if (amountInput?.value) {
    const value = parseFloat(amountInput.value.replace(/,/g, ''));
    if (!isNaN(value)) {
      amount = value;
    }
  }
  
  return {
    title: title || 'Market',
    url,
    side,
    amount,
  };
}

export function isMarketPage(): boolean {
  const url = window.location.href;
  return url.includes('/event/') || url.includes('/market/') || document.querySelector('h1, [data-testid*="title"]') !== null;
}
