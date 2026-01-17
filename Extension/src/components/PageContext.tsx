import { getPageContext } from '../utils/contextData';

export function PageContext(): JSX.Element {
    const context = getPageContext();

    return (
        <div
            style={{
                padding: '12px',
                borderBottom: '1px solid rgba(255,255,255,0.12)',
                background: 'rgba(15,15,18,0.5)',
            }}
        >
            <div style={{ fontSize: 11, opacity: 0.6, textTransform: 'uppercase', marginBottom: 6 }}>
                Current Event
            </div>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4, lineHeight: 1.3 }}>
                {context.title}
            </div>
            <div
                style={{
                    fontSize: 11,
                    opacity: 0.7,
                    wordBreak: 'break-all',
                    marginBottom: 6,
                }}
            >
                {context.url}
            </div>
            <div style={{ fontSize: 10, opacity: 0.5, fontFamily: 'monospace' }}>
                Slug: {context.slug}
            </div>
        </div>
    );
}
