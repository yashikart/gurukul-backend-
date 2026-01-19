import { CognitiveState } from './prana_state_engine.js';

class PranaPacketBuilder {
  constructor(signalCapture, stateEngine, contextProvider) {
    if (!signalCapture) {
      throw new Error('[PRANA] Packet Builder requires SignalCapture instance');
    }
    if (!stateEngine) {
      throw new Error('[PRANA] Packet Builder requires StateEngine instance');
    }

    this.signalCapture = signalCapture;
    this.stateEngine = stateEngine;
    this.contextProvider = contextProvider; // Optional: provides user_id, session_id, lesson_id
    this.apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:3000';

    // Window tracking
    this.windowDuration = 5000; // 5 seconds in milliseconds
    this.windowStart = performance.now();
    
    // Time accounting for current window
    this.timeAccounting = {
      active_ms: 0,
      idle_ms: 0,
      away_ms: 0
    };
    
    // Last known state for tracking
    this.lastState = null;
    this.lastCheckTime = performance.now();
    
    // Packet emission interval
    this._emitInterval = null;
    
    this._init();
  }

  _init() {
    console.log('[PRANA] Packet Builder initialized');
    
    // Start time accounting tracker (checks every 100ms)
    this._startTimeAccounting();
    
    // Emit packets every 5 seconds
    this._emitInterval = setInterval(() => {
      this._emitPacket();
    }, this.windowDuration);
  }

  _startTimeAccounting() {
    // Track time distribution every 100ms
    setInterval(() => {
      const now = performance.now();
      const elapsed = now - this.lastCheckTime;
      const currentState = this.stateEngine.getCurrentState();
      const signals = this.signalCapture.getSignals();
      
      // Categorize time based on current state
      if (currentState === CognitiveState.AWAY || !signals.tab_visible) {
        this.timeAccounting.away_ms += elapsed;
      } else if (currentState === CognitiveState.IDLE || signals.inactivity_ms > 30000) {
        this.timeAccounting.idle_ms += elapsed;
      } else {
        this.timeAccounting.active_ms += elapsed;
      }
      
      this.lastCheckTime = now;
      this.lastState = currentState;
    }, 100);
  }

  _emitPacket() {
    const now = performance.now();
    const windowEnd = now;
    
    // Get current state and signals
    const cognitiveState = this.stateEngine.getCurrentState();
    const signals = this.signalCapture.getSignals();
    
    // Get context (user_id, session_id, lesson_id) from provider if available
    const context = this._getContext();
    
    // Convert time accounting from ms to seconds and ensure sum = 5
    const timeInSeconds = this._normalizeTimeAccounting();
    
    // Calculate deterministic focus score
    const focusScore = this._calculateFocusScore(signals, cognitiveState, timeInSeconds);
    
    // Build PRANA packet
    const packet = {
      // Context fields (from backend or null if not available)
      user_id: context.user_id,
      session_id: context.session_id,
      lesson_id: context.lesson_id,
      
      // Timestamp at window end
      timestamp: new Date().toISOString(),
      
      // Cognitive state from state engine
      cognitive_state: cognitiveState,
      
      // Time accounting (must sum to exactly 5 seconds)
      active_seconds: timeInSeconds.active,
      idle_seconds: timeInSeconds.idle,
      away_seconds: timeInSeconds.away,
      
      // Deterministic focus score
      focus_score: focusScore,
      
      // Raw signals snapshot for this window
      raw_signals: {
        dwell_time_ms: signals.dwell_time_ms,
        hover_loops: signals.hover_loops,
        rapid_click_count: signals.rapid_click_count,
        scroll_depth: signals.scroll_depth,
        mouse_velocity: signals.mouse_velocity,
        inactivity_ms: signals.inactivity_ms,
        tab_visible: signals.tab_visible,
        panel_focused: signals.panel_focused
      }
    };
    
    // Log packet to console
    console.log('[PRANA_PACKET]', packet);
    
    // Reset window for next packet
    this._resetWindow();
    
    return packet;
  }

  _getContext() {
    // Attempt to get context from provider
    if (this.contextProvider && typeof this.contextProvider.getContext === 'function') {
      return this.contextProvider.getContext();
    }
    
    // Try to get user from AuthContext if available
    let userId = null;
    let sessionId = null;
    let lessonId = null;
    
    try {
      // Check if we're in a browser environment with localStorage
      if (typeof window !== 'undefined' && window.localStorage) {
        const token = localStorage.getItem('auth_token');
        
        if (token) {
          // Try to get user_id from stored user info
          try {
            const storedUser = localStorage.getItem('user');
            if (storedUser) {
              const userObj = JSON.parse(storedUser);
              userId = userObj.id || null;
            }
          } catch (e) {
            console.warn('[PRANA] Error parsing stored user:', e);
          }
          
          // Try to get session_id from localStorage
          sessionId = localStorage.getItem('session_id');
          
          // Try to get lesson_id from sessionStorage
          lessonId = sessionStorage.getItem('current_lesson_id');
          
          // Session ID fetching is async, so we'll handle it separately
          // For now, we'll just use what we have locally and fetch async elsewhere
        }
      }
    } catch (e) {
      // localStorage not available or error
      console.warn('[PRANA] Error getting context:', e);
    }
    
    return {
      user_id: userId,
      session_id: sessionId,
      lesson_id: lessonId
    };
  }
  
  async fetchSessionIdFromBackend() {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        return null;
      }
      
      const response = await fetch(`${this.apiBaseUrl}/api/v1/auth/me/session`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.session_id) {
          // Store the session ID in localStorage for future use
          localStorage.setItem('session_id', data.session_id);
          return data.session_id;
        }
      } else {
        console.warn('[PRANA] Failed to fetch session from backend:', response.status);
      }
    } catch (error) {
      console.warn('[PRANA] Error fetching session from backend:', error);
    }
    
    return null;
  }

  _normalizeTimeAccounting() {
    // Convert ms to seconds
    let active = Math.round(this.timeAccounting.active_ms / 100) / 10;
    let idle = Math.round(this.timeAccounting.idle_ms / 100) / 10;
    let away = Math.round(this.timeAccounting.away_ms / 100) / 10;
    
    // Calculate total
    let total = active + idle + away;
    
    // Normalize to exactly 5 seconds (handle rounding errors)
    if (total !== 5.0) {
      const diff = 5.0 - total;
      // Add difference to the largest category
      if (active >= idle && active >= away) {
        active += diff;
      } else if (idle >= away) {
        idle += diff;
      } else {
        away += diff;
      }
      // Round to 1 decimal place
      active = Math.round(active * 10) / 10;
      idle = Math.round(idle * 10) / 10;
      away = Math.round(away * 10) / 10;
    }
    
    return { active, idle, away };
  }

  _calculateFocusScore(signals, cognitiveState, timeInSeconds) {
    /**
     * Deterministic focus score calculation (0-100)
     * 
     * Logic:
     * - Tab not visible → 0
     * - AWAY state → 0
     * - Base score from cognitive state
     * - Adjust for signal quality
     * - Penalize for idle/away time
     */
    
    // If tab not visible or AWAY, focus score is 0
    if (!signals.tab_visible || cognitiveState === CognitiveState.AWAY) {
      return 0;
    }
    
    // Base score from cognitive state
    let baseScore = 0;
    switch (cognitiveState) {
      case CognitiveState.DEEP_FOCUS:
        baseScore = 95;
        break;
      case CognitiveState.ON_TASK:
        baseScore = 75;
        break;
      case CognitiveState.THINKING:
        baseScore = 65;
        break;
      case CognitiveState.DISTRACTED:
        baseScore = 30;
        break;
      case CognitiveState.IDLE:
        baseScore = 10;
        break;
      case CognitiveState.OFF_TASK:
        baseScore = 5;
        break;
      default:
        baseScore = 50;
    }
    
    // Adjust based on signal quality
    let adjustedScore = baseScore;
    
    // High mouse velocity (agitation) reduces focus
    if (signals.mouse_velocity > 2000) {
      adjustedScore -= 10;
    }
    
    // Rapid clicks (anxiety) reduces focus
    if (signals.rapid_click_count >= 3) {
      adjustedScore -= 15;
    }
    
    // Low dwell time reduces focus
    if (signals.dwell_time_ms < 30000) { // Less than 30 seconds
      adjustedScore -= 10;
    }
    
    // Panel not focused reduces score
    if (!signals.panel_focused) {
      adjustedScore -= 20;
    }
    
    // Time distribution penalty
    // More idle/away time = lower focus
    const activeRatio = timeInSeconds.active / 5.0;
    adjustedScore = Math.round(adjustedScore * activeRatio);
    
    // Clamp to 0-100
    return Math.max(0, Math.min(100, adjustedScore));
  }

  _resetWindow() {
    // Reset time accounting for next window
    this.timeAccounting = {
      active_ms: 0,
      idle_ms: 0,
      away_ms: 0
    };
    
    this.windowStart = performance.now();
    this.lastCheckTime = performance.now();
  }

  /**
   * Get the last emitted packet (for testing/debugging)
   * @returns {Object|null} Last packet or null
   */
  getLastPacket() {
    // This would require storing last packet, not implemented yet
    return null;
  }

  /**
   * Register a context provider to supply user_id, session_id, lesson_id
   * @param {Object} provider - Provider with getContext() method
   */
  registerContextProvider(provider) {
    if (provider && typeof provider.getContext === 'function') {
      this.contextProvider = provider;
      console.log('[PRANA] Context provider registered');
    }
  }

  /**
   * Cleanup and stop packet emission
   */
  destroy() {
    if (this._emitInterval) {
      clearInterval(this._emitInterval);
      console.log('[PRANA] Packet Builder stopped');
    }
  }
}

// Module state
let packetBuilderInstance = null;

/**
 * Initialize PRANA Packet Builder
 * @param {Object} signalCapture - SignalCapture instance
 * @param {Object} stateEngine - StateEngine instance
 * @param {Object} contextProvider - Optional context provider
 * @returns {PranaPacketBuilder} Packet builder instance
 */
export function initPacketBuilder(signalCapture, stateEngine, contextProvider = null) {
  if (!packetBuilderInstance) {
    packetBuilderInstance = new PranaPacketBuilder(signalCapture, stateEngine, contextProvider);
  }
  return packetBuilderInstance;
}

/**
 * Get active packet builder instance
 * @returns {PranaPacketBuilder|null} Packet builder instance or null
 */
export function getPacketBuilder() {
  return packetBuilderInstance;
}

export default PranaPacketBuilder;
