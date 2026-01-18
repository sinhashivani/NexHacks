import { LocalProfile, MarketHistoryItem } from '../types/index';

// FLAG #6: KEYWORD MATCHING ASSUMPTION
// ASSUMPTION: Extract topics/entities by matching keywords in market titles
// TEST NEEDED: Verify keyword matching covers actual market titles in Polymarket
// Current implementation: Simple regex-based keyword matching

const TOPIC_KEYWORDS = {
    'Elections': [
        'election', 'voting', 'candidate', 'president', 'senate', 'congressional',
        'democrat', 'republican', 'gop', 'harris', 'trump', 'vote'
    ],
    'Technology': [
        'ai', 'technology', 'tech', 'software', 'crypto', 'blockchain', 'web3',
        'elon', 'meta', 'google', 'apple', 'nvidia', 'tesla'
    ],
    'Finance': [
        'stock', 'market', 'economy', 'recession', 'interest rate', 'fed', 'crypto',
        'bitcoin', 'ethereum', 'sp500', 'nasdaq', 'trading', 'financial'
    ],
    'Politics': [
        'politics', 'political', 'government', 'senate', 'house', 'bill', 'congress',
        'legislation', 'law', 'policy', 'diplomat'
    ],
    'Economy': [
        'economy', 'economic', 'gdp', 'inflation', 'unemployment', 'recession',
        'growth', 'dollar', 'trade', 'tariff', 'wages'
    ],
};

const ENTITY_KEYWORDS = {
    'Trump': ['trump', 'donald trump', 'maga'],
    'Harris': ['harris', 'kamala harris'],
    'Biden': ['biden', 'joe biden'],
    'Elon Musk': ['elon', 'musk', 'elon musk'],
    'Tech Stocks': ['nvidia', 'tesla', 'apple', 'google', 'meta'],
    'Crypto': ['bitcoin', 'ethereum', 'crypto', 'blockchain'],
    'Fed': ['federal reserve', 'fed', 'powell'],
    'China': ['china', 'chinese'],
    'Russia': ['russia', 'russian'],
    'Ukraine': ['ukraine', 'ukrainian'],
};

/**
 * Build LocalProfile from market history
 * FLAG #7: RECENT INTERACTIONS WINDOW ASSUMPTION
 * ASSUMPTION: Use last 50 market interactions (30 days worth at typical usage)
 * TEST NEEDED: Verify appropriate window for meaningful topic/entity extraction
 */
export async function buildLocalProfile(
    history: MarketHistoryItem[]
): Promise<LocalProfile> {
    console.log('[LocalProfile] Building from history:', history.length, 'items');

    // Take most recent 50 interactions
    const recentInteractions = history.slice(-50).map((item) => ({
        title: item.title,
        url: item.url,
        timestamp: item.timestamp,
    }));

    // Extract topic counts
    const topicCounts: Record<string, number> = {};
    recentInteractions.forEach((interaction) => {
        const lowerTitle = interaction.title.toLowerCase();
        Object.entries(TOPIC_KEYWORDS).forEach(([topic, keywords]) => {
            keywords.forEach((keyword) => {
                if (lowerTitle.includes(keyword)) {
                    topicCounts[topic] = (topicCounts[topic] || 0) + 1;
                }
            });
        });
    });

    // Extract entity counts
    const entityCounts: Record<string, number> = {};
    recentInteractions.forEach((interaction) => {
        const lowerTitle = interaction.title.toLowerCase();
        Object.entries(ENTITY_KEYWORDS).forEach(([entity, keywords]) => {
            keywords.forEach((keyword) => {
                if (lowerTitle.includes(keyword)) {
                    entityCounts[entity] = (entityCounts[entity] || 0) + 1;
                }
            });
        });
    });

    // FLAG #8: EMPTY PROFILE FALLBACK ASSUMPTION
    // ASSUMPTION: If no interactions found, return empty counts (not error)
    // TEST NEEDED: Verify API handles empty profiles gracefully
    const profile: LocalProfile = {
        recent_interactions: recentInteractions,
        topic_counts: topicCounts,
        entity_counts: entityCounts,
    };

    console.log('[LocalProfile] Built profile:', {
        interactionCount: recentInteractions.length,
        topicCount: Object.keys(topicCounts).length,
        entityCount: Object.keys(entityCounts).length,
        topics: topicCounts,
        entities: entityCounts,
    });

    return profile;
}

/**
 * Get local profile from storage
 * Convenience function to fetch history from storage and build profile
 */
export async function getLocalProfileFromStorage(): Promise<LocalProfile> {
    try {
        const data = await chrome.storage.local.get('market_history');
        const history: MarketHistoryItem[] = data.market_history || [];
        return buildLocalProfile(history);
    } catch (error) {
        console.error('[LocalProfile] Error getting from storage:', error);
        // FLAG #8: EMPTY PROFILE FALLBACK
        // Return empty profile on error
        return {
            recent_interactions: [],
            topic_counts: {},
            entity_counts: {},
        };
    }
}
