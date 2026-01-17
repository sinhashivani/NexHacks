import React, { useEffect, useRef, useState } from 'react';
import type { CurrentMarket, MarketRecommendation, OverlayState } from '../types';
import { DirectionalIdeas } from './DirectionalIdeas';
import './FloatingAssistant.css';

interface FloatingAssistantProps {
    currentMarket: CurrentMarket;
    state: OverlayState;
    onStateChange: (state: OverlayState) => void;
}

export const FloatingAssistant: React.FC<FloatingAssistantProps> = ({
    currentMarket,
    state,
    onStateChange,
}) => {
    const [isDragging, setIsDragging] = useState(false);
    const [isResizing, setIsResizing] = useState(false);
    const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
    const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0 });
    const assistantRef = useRef<HTMLDivElement>(null);

    const handleHeaderMouseDown = (e: React.MouseEvent) => {
        if ((e.target as HTMLElement).closest('.floating-actions')) {
            return;
        }
        setIsDragging(true);
        setDragOffset({
            x: e.clientX - state.x,
            y: e.clientY - state.y,
        });
    };

    useEffect(() => {
        if (!isDragging) return;

        const handleMouseMove = (e: MouseEvent) => {
            const newX = e.clientX - dragOffset.x;
            const newY = e.clientY - dragOffset.y;

            // Constrain to viewport
            const constrainedX = Math.max(0, Math.min(newX, window.innerWidth - state.width));
            const constrainedY = Math.max(0, Math.min(newY, window.innerHeight - state.height));

            onStateChange({
                ...state,
                x: constrainedX,
                y: constrainedY,
            });
        };

        const handleMouseUp = () => {
            setIsDragging(false);
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging, dragOffset, state, onStateChange]);

    const handleResizeStart = (e: React.MouseEvent) => {
        e.preventDefault();
        setIsResizing(true);
        setResizeStart({
            x: e.clientX,
            y: e.clientY,
            width: state.width,
            height: state.height,
        });
    };

    useEffect(() => {
        if (!isResizing) return;

        const handleMouseMove = (e: MouseEvent) => {
            const deltaX = e.clientX - resizeStart.x;
            const deltaY = e.clientY - resizeStart.y;

            const newWidth = Math.max(280, Math.min(560, resizeStart.width - deltaX));
            const newHeight = Math.max(200, resizeStart.height + deltaY);

            onStateChange({
                ...state,
                width: newWidth,
                height: newHeight,
            });
        };

        const handleMouseUp = () => {
            setIsResizing(false);
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isResizing, resizeStart, state, onStateChange]);

    const handleClose = () => {
        onStateChange({
            ...state,
            open: false,
            minimized: false,
        });
    };

    const handleMinimize = () => {
        onStateChange({
            ...state,
            minimized: !state.minimized,
        });
    };

    const handleAddToBasket = (market: MarketRecommendation) => {
        // Placeholder: In real implementation, would update basket state
        console.log('Add to basket:', market);
    };

    const handleOpenMarket = (url: string) => {
        window.open(url, '_blank');
    };

    if (state.minimized) {
        return (
            <div
                ref={assistantRef}
                className="floating-minimized"
                style={{
                    left: `${state.x}px`,
                    top: `${state.y}px`,
                    width: `${state.width}px`,
                }}
                onMouseDown={handleHeaderMouseDown}
            >
                <div className="floating-minimized-bar">
                    <span>Trade Assistant</span>
                    <div className="floating-actions">
                        <button className="btn-action" onClick={handleMinimize} title="Restore">
                            ⬆
                        </button>
                        <button className="btn-action btn-close" onClick={handleClose} title="Close">
                            ✕
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div
            ref={assistantRef}
            className="floating-assistant"
            style={{
                left: `${state.x}px`,
                top: `${state.y}px`,
                width: `${state.width}px`,
                height: `${state.height}px`,
                cursor: isDragging ? 'grabbing' : 'auto',
            }}
        >
            <div className="floating-header" onMouseDown={handleHeaderMouseDown}>
                <h2>Trade Assistant</h2>
                <div className="floating-actions">
                    <button className="btn-action" onClick={handleMinimize} title="Minimize">
                        −
                    </button>
                    <button className="btn-action btn-close" onClick={handleClose} title="Close">
                        ✕
                    </button>
                </div>
            </div>

            <div className="floating-content">
                <div className="market-context">
                    <div className="market-title">{currentMarket.title || 'Polymarket'}</div>
                    <div className="market-url">{currentMarket.url}</div>
                </div>

                <DirectionalIdeas
                    userSide={currentMarket.side}
                    onAddToBasket={handleAddToBasket}
                    onOpenMarket={handleOpenMarket}
                />
            </div>

            <div
                className="floating-resize-handle"
                onMouseDown={handleResizeStart}
            />
        </div>
    );
};
