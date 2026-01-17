// Placeholder recommendations generator (MVP - no backend)

import type { MarketRecommendation } from '../types';

const SAMPLE_MARKETS: Array<{
  title: string;
  url: string;
  category: 'Finance' | 'Politics' | 'Technology' | 'Elections' | 'Economy';
}> = [
  { title: 'Will Bitcoin reach $100k by end of 2024?', url: 'https://polymarket.com/event/bitcoin-100k-2024', category: 'Finance' },
  { title: 'Will the Fed cut rates by 0.5% in Q2 2024?', url: 'https://polymarket.com/event/fed-rate-cut-q2', category: 'Finance' },
  { title: 'Will Trump win the 2024 presidential election?', url: 'https://polymarket.com/event/trump-2024', category: 'Elections' },
  { title: 'Will Democrats control the Senate in 2025?', url: 'https://polymarket.com/event/senate-2025', category: 'Politics' },
  { title: 'Will AI achieve AGI by 2025?', url: 'https://polymarket.com/event/agi-2025', category: 'Technology' },
  { title: 'Will Apple release AR glasses in 2024?', url: 'https://polymarket.com/event/apple-ar-2024', category: 'Technology' },
  { title: 'Will unemployment rate be below 4% in Q3 2024?', url: 'https://polymarket.com/event/unemployment-q3', category: 'Economy' },
  { title: 'Will inflation drop below 2% by end of 2024?', url: 'https://polymarket.com/event/inflation-2024', category: 'Economy' },
  { title: 'Will there be a recession in 2024?', url: 'https://polymarket.com/event/recession-2024', category: 'Economy' },
  { title: 'Will Tesla stock reach $300 by end of 2024?', url: 'https://polymarket.com/event/tesla-300-2024', category: 'Finance' },
  { title: 'Will OpenAI release GPT-5 in 2024?', url: 'https://polymarket.com/event/gpt5-2024', category: 'Technology' },
  { title: 'Will the UK hold a general election in 2024?', url: 'https://polymarket.com/event/uk-election-2024', category: 'Politics' },
  { title: 'Will the S&P 500 close above 5000 in 2024?', url: 'https://polymarket.com/event/sp500-5000-2024', category: 'Finance' },
  { title: 'Will Russia-Ukraine conflict end in 2024?', url: 'https://polymarket.com/event/ukraine-2024', category: 'Politics' },
  { title: 'Will Google release a ChatGPT competitor in 2024?', url: 'https://polymarket.com/event/google-ai-2024', category: 'Technology' },
];

const REASONS = [
  'High correlation with current market trends',
  'Similar topic and entity overlap',
  'Strong historical performance pattern',
  'Complementary market for portfolio diversification',
  'Related to current economic indicators',
  'Matches your recent market interests',
  'High liquidity and trading volume',
  'Similar risk profile to primary market',
];

function randomChoice<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)];
}

function shuffle<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

export function generateAmplifyRecommendations(currentUrl: string): MarketRecommendation[] {
  // Filter out current market
  const available = SAMPLE_MARKETS.filter(m => m.url !== currentUrl);
  
  // Shuffle and take 5
  const selected = shuffle(available).slice(0, 5);
  
  return selected.map((market, index) => ({
    id: `amp-${Date.now()}-${index}`,
    title: market.title,
    url: market.url,
    category: market.category,
    score: 0.6 + Math.random() * 0.3, // 0.6 to 0.9
    reason: randomChoice(REASONS),
  }));
}

export function generateHedgeRecommendations(currentUrl: string): MarketRecommendation[] {
  // Filter out current market
  const available = SAMPLE_MARKETS.filter(m => m.url !== currentUrl);
  
  // Shuffle and take 5
  const selected = shuffle(available).slice(0, 5);
  
  return selected.map((market, index) => ({
    id: `hedge-${Date.now()}-${index}`,
    title: market.title,
    url: market.url,
    category: market.category,
    score: 0.5 + Math.random() * 0.3, // 0.5 to 0.8
    reason: randomChoice(REASONS),
  }));
}
