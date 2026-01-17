import React, { useEffect, useRef, useState } from 'react';
import type { CurrentMarket, MarketRecommendation, OverlayState } from '../types';
import { ContextHeader } from './ContextHeader';
import { DirectionalIdeas } from './DirectionalIdeas';
import './FloatingAssistant.css';

interface FloatingAssistantProps {
    currentMarket: CurrentMarket;
    state: OverlayState;
    onStateChange: (state: Partial<OverlayState>) => void;
}

export const FloatingAssistant: React.FC<FloatingAssistantProps> = ({
    currentMarket,
    state,
    onStateChange,
}) => {
    const [isDragging, setIsDragging] = useState(false);
    const [isResizing, setIsResizing] = useState(false);
    const [dragStart, setDragStart] = useState({ clientX: 0, clientY: 0 });
    const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0, clientX: 0, clientY: 0 });
    const assistantRef = useRef<HTMLDivElement>(null);
    const headerRef = useRef<HTMLDivElement>(null);

    /**
     * Handle pointer down on header - only for floating mode drag
     */
    const handleHeaderPointerDown = (e: React.PointerEvent) => {
        // Skip if clicking action buttons
        if ((e.target as HTMLElement).closest('.floating-actions')) {
            return;
        }

        // Only allow drag in floating mode
        if (state.layoutMode !== 'floating') {
            return;
        }

        console.debug('[CONTENT] Drag started');
        setIsDragging(true);
        setDragStart({ clientX: e.clientX, clientY: e.clientY });

        // Capture pointer for this element
        if (headerRef.current) {
            headerRef.current.setPointerCapture(e.pointerId);
        }
    };

    /**
     * Handle pointer move during drag - update position
     */
    useEffect(() => {
        if (!isDragging || !assistantRef.current || state.layoutMode !== 'floating') return;

        const handlePointerMove = (e: PointerEvent) => {
            const deltaX = e.clientX - dragStart.clientX;
            const deltaY = e.clientY - dragStart.clientY;

            const newX = state.x + deltaX;
            const newY = state.y + deltaY;

            // Constrain to viewport
            const constrainedX = Math.max(0, Math.min(newX, window.innerWidth - state.width));
            const constrainedY = Math.max(0, Math.min(newY, window.innerHeight - state.height));

            onStateChange({
                x: constrainedX,
                y: constrainedY,
            });

            setDragStart({ clientX: e.clientX, clientY: e.clientY });
        };

        const handlePointerUp = (e: PointerEvent) => {
            console.debug('[CONTENT] Drag ended');
            setIsDragging(false);
            if (headerRef.current) {
                try {
                    headerRef.current.releasePointerCapture(e.pointerId);
                } catch (err) {
                    // Already released
                }
            }
        };

        document.addEventListener('pointermove', handlePointerMove, { passive: true });
        document.addEventListener('pointerup', handlePointerUp, { passive: true });

        return () => {
            document.removeEventListener('pointermove', handlePointerMove);
            document.removeEventListener('pointerup', handlePointerUp);
        };
    }, [isDragging, dragStart, state, onStateChange]);

    /**
     * Handle pointer down on resize handle - only for floating mode
     */
    const handleResizePointerDown = (e: React.PointerEvent) => {
        if (state.layoutMode !== 'floating') {
            return;
        }

        e.preventDefault();
        console.debug('[CONTENT] Resize started');
        setIsResizing(true);
        setResizeStart({
            x: state.x,
            y: state.y,
            width: state.width,
            height: state.height,
            clientX: e.clientX,
            clientY: e.clientY,
        });

        if (assistantRef.current) {
            assistantRef.current.setPointerCapture(e.pointerId);
        }
    };

    /**
     * Handle pointer move during resize
     */
    useEffect(() => {
        if (!isResizing || state.layoutMode !== 'floating') return;

        const handlePointerMove = (e: PointerEvent) => {
            const deltaX = e.clientX - resizeStart.clientX;
            const deltaY = e.clientY - resizeStart.clientY;

            const newWidth = Math.max(280, Math.min(560, resizeStart.width - deltaX));
            const newHeight = Math.max(200, resizeStart.height + deltaY);

            onStateChange({
                width: newWidth,
                height: newHeight,
            });
        };

        const handlePointerUp = (e: PointerEvent) => {
            console.debug('[CONTENT] Resize ended');
            setIsResizing(false);
            if (assistantRef.current) {
                try {
                    assistantRef.current.releasePointerCapture(e.pointerId);
                } catch (err) {
                    // Already released
                }
            }
        };

        document.addEventListener('pointermove', handlePointerMove, { passive: true });
        document.addEventListener('pointerup', handlePointerUp, { passive: true });

        return () => {
            document.removeEventListener('pointermove', handlePointerMove);
            document.removeEventListener('pointerup', handlePointerUp);
        };
    }, [isResizing, resizeStart, state, onStateChange]);

    const handleClose = () => {
        console.debug('[CONTENT] Close button clicked');
        onStateChange({ open: false });
    };

    const handleAddToBasket = (market: MarketRecommendation) => {
        console.log('Add to basket:', market);
    };

    const handleOpenMarket = (url: string) => {
        window.open(url, '_blank');
    };

    // Only show resize handle in floating mode
    const showResizeHandle = state.layoutMode === 'floating';

    // Determine if we should use two-column layout (only in docked mode with sufficient width)
    const useTwoColumnLayout = state.layoutMode === 'docked' && state.width >= 600;

    return (
        <div
            ref={assistantRef}
            className="floating-assistant"
            style={{
                width: `${state.width}px`,
                height: state.layoutMode === 'docked' ? 'auto' : `${state.height}px`,
                cursor: isDragging ? 'grabbing' : isResizing ? 'se-resize' : 'auto',
                userSelect: isDragging ? 'none' : 'auto',
                display: 'flex',
                flexDirection: 'column',
            }}
        >
            <div
                ref={headerRef}
                className="floating-header"
                onPointerDown={handleHeaderPointerDown}
                style={{
                    cursor: state.layoutMode === 'floating' ? (isDragging ? 'grabbing' : 'grab') : 'default',
                }}
            >
                <h2>Trade Assistant</h2>
                <div className="floating-actions">
                    <button className="btn-action btn-close" onClick={handleClose} title="Close">
                        ✕
                    </button>
                </div>
            </div>

            {/* Two-Column Layout */}
            {useTwoColumnLayout ? (
                <div
                    style={{
                        display: 'flex',
                        flex: 1,
                        overflow: 'hidden',
                    }}
                >
                    {/* Left Column: Context (30%) */}
                    <div
                        style={{
                            width: '30%',
                            overflowY: 'auto',
                            borderRight: '1px solid rgba(255,255,255,0.08)',
                        }}
                    >
                        <ContextHeader />
                    </div>

                    {/* Right Column: Similar Trades (70%) */}
                    <div
                        style={{
                            width: '70%',
                            overflowY: 'auto',
                            overflow: 'hidden',
                        }}
                    >
                        <DirectionalIdeas
                            userSide={currentMarket.side}
                            onAddToBasket={handleAddToBasket}
                            onOpenMarket={handleOpenMarket}
                        />
                    </div>
                </div>
            ) : (
                /* Single Column Layout (default) */
                <div
                    className="floating-content"
                    style={{
                        flex: 1,
                        overflow: 'auto',
                    }}
                >
                    <ContextHeader />

                    <div
                        className="market-context"
                        style={{
                            padding: '12px',
                            borderBottom: '1px solid rgba(255,255,255,0.12)',
                        }}
                    >
                        <div className="market-title">{currentMarket.title || 'Polymarket'}</div>
                        <div className="market-url">{currentMarket.url}</div>
                    </div>

                    <DirectionalIdeas
                        userSide={currentMarket.side}
                        onAddToBasket={handleAddToBasket}
                        onOpenMarket={handleOpenMarket}
                    />
                </div>
            )}

            {showResizeHandle && (
                <div
                    className="floating-resize-handle"
                    onPointerDown={handleResizePointerDown}
                    style={{
                        cursor: isResizing ? 'se-resize' : 'se-resize',
                    }}
                />
            )}
        </div>
    );
};
