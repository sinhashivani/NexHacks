// Overlay state store - single source of truth with chrome.storage.sync

import type { OverlayState } from '../types';
import { getOverlayState, saveOverlayState } from './storage';

type StateChangeListener = (state: OverlayState) => void;

class OverlayStore {
  private state: OverlayState | null = null;
  private listeners: Set<StateChangeListener> = new Set();
  private initialized = false;
  private saveDebounceTimer: NodeJS.Timeout | null = null;
  private lastSavedState: Partial<OverlayState> = {};

  async init(): Promise<OverlayState> {
    if (this.initialized && this.state) {
      console.debug('[STORE] Already initialized, returning cached state');
      return this.state;
    }

    console.debug('[STORE] Initializing overlayStore from storage');
    this.state = await getOverlayState();
    this.initialized = true;
    this.lastSavedState = { open: this.state.open, x: this.state.x, y: this.state.y };
    console.debug('[STORE] Initialized with state:', this.state);
    return this.state;
  }

  getState(): OverlayState | null {
    return this.state;
  }

  /**
   * Update state locally and debounce persistence.
   * Only persists {open, x, y} if they changed.
   */
  setState(newState: Partial<OverlayState>): void {
    if (!this.state) {
      console.warn('[STORE] setState called before init');
      return;
    }

    const prevState = { ...this.state };
    this.state = { ...this.state, ...newState };

    console.debug('[STORE] State updated:', this.state);

    // Notify listeners immediately for responsive UI
    this.notifyListeners();

    // Debounce persistence - only save {open, x, y}
    this.debounceAndSave(newState);
  }

  /**
   * Open/close the overlay
   */
  async setOpen(open: boolean): Promise<void> {
    console.debug('[STORE] setOpen:', open);
    if (!this.state) {
      await this.init();
    }
    if (this.state) {
      this.setState({ open });
    }
  }

  /**
   * Update position and size (e.g., during drag/resize)
   */
  setPosition(x: number, y: number, width?: number, height?: number): void {
    console.debug('[STORE] setPosition:', { x, y, width, height });
    if (!this.state) return;

    const update: Partial<OverlayState> = { x, y };
    if (width !== undefined) update.width = width;
    if (height !== undefined) update.height = height;

    this.setState(update);
  }

  /**
   * Debounce persistence of {open, x, y} to avoid MAX_WRITE_OPERATIONS
   */
  private debounceAndSave(changes: Partial<OverlayState>): void {
    // Clear previous timer
    if (this.saveDebounceTimer) {
      clearTimeout(this.saveDebounceTimer);
    }

    // Only track {open, x, y} changes for persistence
    const persistableChanges = ['open', 'x', 'y'] as const;
    let hasPersistedChange = false;

    for (const key of persistableChanges) {
      if (key in changes && this.lastSavedState[key] !== (this.state as any)?.[key]) {
        hasPersistedChange = true;
        break;
      }
    }

    if (!hasPersistedChange) {
      console.debug('[STORE] No persistable changes (only width/height), skipping save');
      return;
    }

    // Set debounce timer - save after 500ms of inactivity
    this.saveDebounceTimer = setTimeout(async () => {
      if (this.state) {
        const persistedState = {
          open: this.state.open,
          x: this.state.x,
          y: this.state.y,
          width: this.state.width,
          height: this.state.height,
        };

        console.debug('[STORE] Saving persisted state:', persistedState);
        await saveOverlayState(persistedState);

        // Update last saved state
        this.lastSavedState = { open: this.state.open, x: this.state.x, y: this.state.y };
      }
      this.saveDebounceTimer = null;
    }, 500);
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