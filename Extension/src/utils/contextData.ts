/**
 * Mock context data for outlets and analyst opinions
 */

export type OutletStance = 'Support' | 'Neutral' | 'Oppose';

export interface Outlet {
    name: string;
    stance: OutletStance;
    confidence: number; // 0-100
    rationale: string;
    url: string;
}

export interface Analyst {
    name: string;
    role: string;
    quote: string;
}

export interface PageContext {
    title: string;
    url: string;
    slug: string;
}

export const MOCK_OUTLETS: Outlet[] = [
    {
        name: 'WSJ',
        stance: 'Support',
        confidence: 85,
        rationale: 'Recent analysis aligns with the bullish macro thesis.',
        url: 'https://wsj.com',
    },
    {
        name: 'Bloomberg',
        stance: 'Support',
        confidence: 78,
        rationale: 'Market momentum indicators favor upside momentum.',
        url: 'https://bloomberg.com',
    },
    {
        name: 'Reuters',
        stance: 'Neutral',
        confidence: 65,
        rationale: 'Mixed signals from economic data and trading flows.',
        url: 'https://reuters.com',
    },
    {
        name: 'Financial Times',
        stance: 'Neutral',
        confidence: 72,
        rationale: 'Consensus suggests wait-and-see on catalyst timing.',
        url: 'https://ft.com',
    },
    {
        name: 'CNBC',
        stance: 'Oppose',
        confidence: 68,
        rationale: 'Valuation concerns outweigh near-term catalysts.',
        url: 'https://cnbc.com',
    },
    {
        name: 'The Economist',
        stance: 'Oppose',
        confidence: 75,
        rationale: 'Structural headwinds suggest caution on direction.',
        url: 'https://economist.com',
    },
];

export const MOCK_ANALYSTS: Analyst[] = [
    {
        name: 'A. Chen',
        role: 'Macro Analyst',
        quote: 'Fed policy pivot creates structural tailwind for equities this cycle.',
    },
    {
        name: 'M. Rivera',
        role: 'Rates Trader',
        quote: 'Curve inversion signals turn around—duration is attractive.',
    },
    {
        name: 'S. Patel',
        role: 'Crypto PM',
        quote: 'Regulatory clarity + retail inflow = strong accumulation phase.',
    },
    {
        name: 'J. Wong',
        role: 'Tech Analyst',
        quote: 'AI capex cycle remains intact; near-term pullback is a buying opportunity.',
    },
];

/**
 * Extract slug from URL or title
 */
export function extractSlug(url: string, title: string): string {
    try {
        const urlObj = new URL(url);
        const pathname = urlObj.pathname.toLowerCase();
        const titleSlug = title.toLowerCase().replace(/\s+/g, '-').substring(0, 30);

        // Try to extract market identifier from URL
        if (pathname.includes('market') || pathname.includes('event')) {
            const matches = pathname.match(/([a-z0-9-]+)/g);
            if (matches && matches.length > 0) {
                return matches[matches.length - 1];
            }
        }

        return titleSlug;
    } catch {
        return title.toLowerCase().replace(/\s+/g, '-').substring(0, 30);
    }
}

/**
 * Generate keyword-based outlets for context
 * If slug contains "fed" show macro-friendly outlets, etc.
 */
export function getContextualOutlets(slug: string): Outlet[] {
    // Default: return all
    if (!slug) return MOCK_OUTLETS;

    // Just return all for now; could customize by keywords in future
    return MOCK_OUTLETS.sort((a, b) => b.confidence - a.confidence);
}

export function getContextualAnalysts(_slug: string): Analyst[] {
    return MOCK_ANALYSTS;
}

export function getPageContext(): PageContext {
    return {
        title: document.title,
        url: location.href,
        slug: extractSlug(location.href, document.title),
    };
}
