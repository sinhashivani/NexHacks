import React, { useState, useEffect } from 'react';
import {
  getPinnedOrders,
  savePinnedOrder,
  removePinnedOrder,
  reorderPinnedOrder,
} from '../utils/storage';
import type { PinnedOrder } from '../types';
import './PinnedOrders.css';

export const PinnedOrders: React.FC = () => {
  const [orders, setOrders] = useState<PinnedOrder[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editNotes, setEditNotes] = useState('');

  useEffect(() => {
    loadOrders();
  }, []);

  async function loadOrders() {
    const saved = await getPinnedOrders();
    setOrders(saved);
  }

  async function handlePinCurrent() {
    const title = document.querySelector('h1')?.textContent?.trim() || 'Market';
    const url = window.location.href;
    
    const newOrder: PinnedOrder = {
      id: `pin-${Date.now()}`,
      title,
      url,
      timestamp: Date.now(),
      notes: '',
    };
    
    const updated = [...orders, newOrder];
    setOrders(updated);
    await savePinnedOrder(newOrder);
  }

  async function handleRemove(id: string) {
    const updated = orders.filter(o => o.id !== id);
    setOrders(updated);
    await removePinnedOrder(id);
  }

  async function handleReorder(id: string, direction: 'up' | 'down') {
    await reorderPinnedOrder(id, direction);
    await loadOrders();
  }

  function handleEditStart(order: PinnedOrder) {
    setEditingId(order.id);
    setEditNotes(order.notes);
  }

  async function handleEditSave(id: string) {
    const updated = orders.map(o =>
      o.id === id ? { ...o, notes: editNotes } : o
    );
    setOrders(updated);
    await chrome.storage.sync.set({ pinned_orders: updated });
    setEditingId(null);
  }

  function handleEditCancel() {
    setEditingId(null);
    setEditNotes('');
  }

  return (
    <div className="pinned-orders-section">
      <div className="pinned-header">
        <h3>Pinned Orders</h3>
        <button className="btn-pin-current" onClick={handlePinCurrent}>
          Pin Current
        </button>
      </div>

      {orders.length === 0 ? (
        <div className="pinned-empty">No pinned orders</div>
      ) : (
        <div className="pinned-list">
          {orders.map((order, index) => (
            <div key={order.id} className="pinned-item">
              <div className="pinned-item-header">
                <div className="pinned-item-title">{order.title}</div>
                <div className="pinned-item-actions">
                  {index > 0 && (
                    <button
                      className="btn-reorder"
                      onClick={() => handleReorder(order.id, 'up')}
                      title="Move up"
                    >
                      ↑
                    </button>
                  )}
                  {index < orders.length - 1 && (
                    <button
                      className="btn-reorder"
                      onClick={() => handleReorder(order.id, 'down')}
                      title="Move down"
                    >
                      ↓
                    </button>
                  )}
                  <button
                    className="btn-open-pinned"
                    onClick={() => window.open(order.url, '_blank')}
                    title="Open in new tab"
                  >
                    Open
                  </button>
                  <button
                    className="btn-remove-pinned"
                    onClick={() => handleRemove(order.id)}
                    title="Remove"
                  >
                    ×
                  </button>
                </div>
              </div>
              
              <div className="pinned-item-url">{order.url}</div>
              
              {order.side && (
                <div className="pinned-item-side">Side: {order.side}</div>
              )}
              {order.amount !== undefined && (
                <div className="pinned-item-amount">Amount: ${order.amount}</div>
              )}
              
              <div className="pinned-item-notes">
                {editingId === order.id ? (
                  <div className="notes-edit">
                    <textarea
                      value={editNotes}
                      onChange={(e) => setEditNotes(e.target.value)}
                      placeholder="Add notes..."
                      rows={2}
                    />
                    <div className="notes-actions">
                      <button onClick={() => handleEditSave(order.id)}>Save</button>
                      <button onClick={handleEditCancel}>Cancel</button>
                    </div>
                  </div>
                ) : (
                  <div className="notes-display">
                    {order.notes || <span className="notes-placeholder">No notes</span>}
                    <button
                      className="btn-edit-notes"
                      onClick={() => handleEditStart(order)}
                    >
                      {order.notes ? 'Edit' : 'Add Notes'}
                    </button>
                  </div>
                )}
              </div>
              
              <div className="pinned-item-timestamp">
                {new Date(order.timestamp).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
