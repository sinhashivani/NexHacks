import React, { useMemo, useState } from 'react';
import type { MarketRecommendation } from '../types';
import './DirectionalIdeas.css';

interface DirectionalIdeasProps {
    userSide?: 'YES' | 'NO';
    onAddToBasket: (market: MarketRecommendation) => void;
    onOpenMarket: (url: string) => void;
}

const SAMPLE_MARKETS = [
    { id: '1', title: 'Will Bitcoin reach $100k by end of 2025?', category: 'Finance' as const },
    { id: '2', title: 'Will US GDP grow above 2% in Q1 2025?', category: 'Economy' as const },
    { id: '3', title: 'Will Federal Reserve cut rates in Q2 2025?', category: 'Finance' as const },
    { id: '4', title: 'Will Trump be re-elected in 2026?', category: 'Politics' as const },
    { id: '5', title: 'Will AI surpass human intelligence by 2030?', category: 'Technology' as const },
    { id: '6', title: 'Will tech stocks outperform S&P 500 in 2025?', category: 'Finance' as const },
    { id: '7', title: 'Will inflation remain above 3% by mid-2025?', category: 'Economy' as const },
    { id: '8', title: 'Will a new AI breakthrough occur by Q4 2025?', category: 'Technology' as const },
    { id: '9', title: 'Will the 2026 midterms see record turnout?', category: 'Elections' as const },
    { id: '10', title: 'Will green energy investments exceed $500B in 2025?', category: 'Economy' as const },
];

const YES_REASONS = [
    'Similar YES exposure with positive correlation',
    'Complements current YES position risk profile',
    'Historical data suggests positive co-movement',
    'Hedges against specific downside risk',
    'Amplifies bullish market thesis',
];

const NO_REASONS = [
    'Similar NO exposure with positive correlation',
    'Complements current NO position risk profile',
    'Historical data suggests negative co-movement',
    'Hedges against specific upside risk',
    'Amplifies bearish market thesis',
];

export const DirectionalIdeas: React.FC<DirectionalIdeasProps> = ({
    userSide,
    onAddToBasket,
    onOpenMarket,
}) => {
    const [scoreCache] = useState<Record<string, number>>(() => {
        const cache: Record<string, number> = {};
        SAMPLE_MARKETS.forEach(m => {
            cache[m.id] = Math.random() * 0.4 + 0.5; // Scores between 0.5-0.9
        });
        return cache;
    });

    const yesList = useMemo(() => {
        return SAMPLE_MARKETS.slice(0, 5).map((m, idx) => ({
            ...m,
            score: scoreCache[m.id],
            reason: YES_REASONS[idx % YES_REASONS.length],
            url: `https://polymarket.com/market/${m.id}`,
        }));
    }, [scoreCache]);

    const noList = useMemo(() => {
        return SAMPLE_MARKETS.slice(5, 10).map((m, idx) => ({
            ...m,
            score: scoreCache[m.id],
            reason: NO_REASONS[idx % NO_REASONS.length],
            url: `https://polymarket.com/market/${m.id}`,
        }));
    }, [scoreCache]);

    return (
        <div className="directional-ideas">
            <div className="directional-header">Directional Ideas</div>

            {/* YES Panel */}
            <div className={`directional-panel ${userSide === 'YES' ? 'emphasized' : ''}`}>
                <div className="directional-panel-header">
                    <span className="directional-panel-title">If you like YES (Buy)</span>
                    <span className="directional-count">{yesList.length}</span>
                </div>
                <div className="directional-list">
                    {yesList.map(market => (
                        <div key={market.id} className="directional-item">
                            <div className="directional-item-title">{market.title}</div>
                            <div className="directional-item-meta">
                                <span className={`directional-category ${market.category.toLowerCase()}`}>
                                    {market.category}
                                </span>
                                <span className="directional-score">{(market.score * 100).toFixed(0)}%</span>
                            </div>
                            <div className="directional-reason">{market.reason}</div>
                            <div className="directional-actions">
                                <button
                                    className="btn-open"
                                    onClick={() => onOpenMarket(market.url)}
                                >
                                    Open
                                </button>
                                <button
                                    className="btn-add"
                                    onClick={() => onAddToBasket(market)}
                                >
                                    Add to basket
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* NO Panel */}
            <div className={`directional-panel ${userSide === 'NO' ? 'emphasized' : ''}`}>
                <div className="directional-panel-header">
                    <span className="directional-panel-title">If you like NO (Sell)</span>
                    <span className="directional-count">{noList.length}</span>
                </div>
                <div className="directional-list">
                    {noList.map(market => (
                        <div key={market.id} className="directional-item">
                            <div className="directional-item-title">{market.title}</div>
                            <div className="directional-item-meta">
                                <span className={`directional-category ${market.category.toLowerCase()}`}>
                                    {market.category}
                                </span>
                                <span className="directional-score">{(market.score * 100).toFixed(0)}%</span>
                            </div>
                            <div className="directional-reason">{market.reason}</div>
                            <div className="directional-actions">
                                <button
                                    className="btn-open"
                                    onClick={() => onOpenMarket(market.url)}
                                >
                                    Open
                                </button>
                                <button
                                    className="btn-add"
                                    onClick={() => onAddToBasket(market)}
                                >
                                    Add to basket
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};
