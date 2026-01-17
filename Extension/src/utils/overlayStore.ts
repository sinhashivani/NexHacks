// Overlay state store - single source of truth with chrome.storage.sync

import type { OverlayState } from '../types';
import { getOverlayState, saveOverlayState } from './storage';

type StateChangeListener = (state: OverlayState) => void;

class OverlayStore {
  private state: OverlayState | null = null;
  private listeners: Set<StateChangeListener> = new Set();
  private initialized = false;

  async init(): Promise<OverlayState> {
    if (this.initialized && this.state) {
      console.debug('[STORE] Already initialized, returning cached state');
      return this.state;
    }

    console.debug('[STORE] Initializing overlayStore from storage');
    this.state = await getOverlayState();
    this.initialized = true;
    console.debug('[STORE] Initialized with state:', this.state);
    return this.state;
  }

  getState(): OverlayState | null {
    return this.state;
  }

  async setState(newState: OverlayState): Promise<void> {
    console.debug('[STORE] Setting state:', newState);
    this.state = newState;
    await saveOverlayState(newState);
    console.debug('[STORE] State saved to storage, notifying listeners');
    this.notifyListeners();
  }

  async toggleOverlay(): Promise<void> {
    console.debug('[STORE] toggleOverlay() called');
    if (!this.state) {
      console.debug('[STORE] No state, initializing first');
      await this.init();
    }

    if (!this.state) {
      console.debug('[STORE] Still no state after init, returning');
      return;
    }

    console.debug('[STORE] Current state before toggle:', this.state);

    if (!this.state.open) {
      // Closed -> Open (and un-minimize)
      console.debug('[STORE] Toggling: closed -> open');
      await this.setState({
        ...this.state,
        open: true,
        minimized: false,
      });
    } else if (this.state.minimized) {
      // Minimized -> Expand (open + not minimized)
      console.debug('[STORE] Toggling: minimized -> expanded');
      await this.setState({
        ...this.state,
        open: true,
        minimized: false,
      });
    } else {
      // Open and not minimized -> Close
      console.debug('[STORE] Toggling: open -> closed');
      await this.setState({
        ...this.state,
        open: false,
        minimized: false,
      });
    }
  }

  subscribe(listener: StateChangeListener): () => void {
    console.debug('[STORE] Adding state change listener');
    this.listeners.add(listener);
    return () => {
      console.debug('[STORE] Removing state change listener');
      this.listeners.delete(listener);
    };
  }

  private notifyListeners(): void {
    console.debug('[STORE] Notifying', this.listeners.size, 'listeners');
    if (this.state) {
      this.listeners.forEach((listener, index) => {
        console.debug('[STORE] Calling listener', index);
        try {
          listener(this.state!);
        } catch (error) {
          console.error('[STORE] Error in listener:', error);
        }
      });
    }
  }
}

// Singleton instance
export const overlayStore = new OverlayStore();