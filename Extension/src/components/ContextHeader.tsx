import { getContextualAnalysts, getContextualOutlets, getPageContext } from '../utils/contextData';

export function ContextHeader(): JSX.Element {
    const context = getPageContext();
    const outlets = getContextualOutlets(context.slug);
    const analysts = getContextualAnalysts(context.slug);

    const getStanceColor = (stance: string): string => {
        switch (stance) {
            case 'Support':
                return '#4caf50';
            case 'Oppose':
                return '#f44336';
            case 'Neutral':
            default:
                return '#ff9800';
        }
    };

    const handleOutletClick = (url: string) => {
        // Use chrome.runtime.sendMessage to background to safely open URL
        chrome.runtime.sendMessage(
            { action: 'openUrl', url },
            (response) => {
                if (response?.success) {
                    console.debug('[CONTEXT] Opened outlet URL:', url);
                } else {
                    // Fallback: try window.open (may be blocked)
                    try {
                        window.open(url, '_blank', 'noopener,noreferrer');
                    } catch (err) {
                        console.warn('[CONTEXT] Could not open URL:', url);
                    }
                }
            }
        );
    };

    return (
        <div
            style={{
                padding: '12px',
                borderBottom: '1px solid rgba(255,255,255,0.12)',
                background: 'rgba(15,15,18,0.95)',
                position: 'sticky',
                top: 0,
                zIndex: 10,
            }}
        >
            {/* Current Event - Condensed */}
            <div style={{ marginBottom: 10 }}>
                <div style={{ fontSize: 10, opacity: 0.6, textTransform: 'uppercase', marginBottom: 4 }}>
                    Current Event
                </div>
                <div
                    style={{
                        fontSize: 12,
                        fontWeight: 600,
                        marginBottom: 3,
                        lineHeight: 1.2,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                    }}
                >
                    {context.title}
                </div>
                <div
                    style={{
                        fontSize: 9,
                        opacity: 0.5,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                    }}
                >
                    {context.url}
                </div>
            </div>

            {/* Outlet Stance - Compact Source Boxes */}
            <div style={{ marginBottom: 10 }}>
                <div style={{ fontSize: 10, opacity: 0.6, textTransform: 'uppercase', marginBottom: 6 }}>
                    Sources
                </div>
                <div
                    style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(70px, 1fr))',
                        gap: '6px',
                    }}
                >
                    {outlets.slice(0, 6).map((outlet, idx) => (
                        <div
                            key={idx}
                            onClick={() => handleOutletClick(outlet.url)}
                            title={outlet.url}
                            style={{
                                padding: '6px 8px',
                                borderRadius: '5px',
                                background: 'rgba(255,255,255,0.06)',
                                border: `1.5px solid ${getStanceColor(outlet.stance)}`,
                                cursor: 'pointer',
                                transition: 'all 0.2s ease',
                                userSelect: 'none',
                                textAlign: 'center',
                            }}
                            onMouseEnter={(e) => {
                                const el = e.currentTarget as HTMLDivElement;
                                el.style.background = 'rgba(255,255,255,0.12)';
                                el.style.transform = 'translateY(-2px)';
                                el.style.boxShadow = `0 2px 8px rgba(${outlet.stance === 'Support' ? '76, 175, 80' : outlet.stance === 'Oppose' ? '244, 67, 54' : '255, 152, 0'
                                    }, 0.3)`;
                            }}
                            onMouseLeave={(e) => {
                                const el = e.currentTarget as HTMLDivElement;
                                el.style.background = 'rgba(255,255,255,0.06)';
                                el.style.transform = 'translateY(0)';
                                el.style.boxShadow = 'none';
                            }}
                        >
                            <div style={{ fontSize: 11, fontWeight: 700, marginBottom: 3 }}>
                                {outlet.name}
                            </div>
                            <div
                                style={{
                                    fontSize: 9,
                                    color: getStanceColor(outlet.stance),
                                    fontWeight: 600,
                                    marginBottom: 2,
                                }}
                            >
                                {outlet.stance}
                            </div>
                            <div
                                style={{
                                    fontSize: 8,
                                    opacity: 0.6,
                                }}
                            >
                                {outlet.confidence}%
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Key Voices - Condensed */}
            <div>
                <div style={{ fontSize: 10, opacity: 0.6, textTransform: 'uppercase', marginBottom: 6 }}>
                    Key Voices
                </div>
                <div style={{ display: 'grid', gap: 5 }}>
                    {analysts.slice(0, 2).map((analyst, idx) => (
                        <div
                            key={idx}
                            style={{
                                padding: '6px 8px',
                                borderRadius: '5px',
                                background: 'rgba(255,255,255,0.04)',
                                fontSize: 9,
                            }}
                        >
                            <div
                                style={{
                                    fontWeight: 600,
                                    marginBottom: 3,
                                    fontSize: 10,
                                }}
                            >
                                {analyst.name}{' '}
                                <span style={{ fontSize: 8, opacity: 0.5, fontWeight: 'normal' }}>
                                    ({analyst.role})
                                </span>
                            </div>
                            <div
                                style={{
                                    opacity: 0.7,
                                    lineHeight: 1.3,
                                    fontStyle: 'italic',
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                    display: '-webkit-box',
                                    WebkitLineClamp: 2,
                                    WebkitBoxOrient: 'vertical',
                                }}
                            >
                                "{analyst.quote}"
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

