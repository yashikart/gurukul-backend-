export const CognitiveState = {
  ON_TASK: 'ON_TASK',
  THINKING: 'THINKING',
  IDLE: 'IDLE',
  DISTRACTED: 'DISTRACTED',
  AWAY: 'AWAY',
  OFF_TASK: 'OFF_TASK',
  DEEP_FOCUS: 'DEEP_FOCUS'
};

class PranaCognitiveStateEngine {
  constructor(signalCapture) {
    if (!signalCapture) {
      throw new Error('[PRANA] State Engine requires SignalCapture instance');
    }

    this.signalCapture = signalCapture;
    
    // Current state tracking
    this.currentState = CognitiveState.ON_TASK;
    this.stateEntryTime = performance.now();
    this.lastStateChangeTime = performance.now();
    
    // State history
    this.transitionLog = [];
    
    // Cooldown configuration (milliseconds)
    this.cooldowns = {
      minimum: 5000,           // 5 seconds minimum before any state change
      deepFocusEntry: 15000    // 15 seconds sustained condition for DEEP_FOCUS
    };
    
    // Deep focus tracking
    this._deepFocusCandidate = false;
    this._deepFocusCandidateTime = null;
    
    // Evaluation interval
    this._evaluationInterval = null;
    
    this._init();
  }

  _init() {
    // Log initial state
    console.log('[PRANA] Cognitive State Engine initialized');
    console.log(`[PRANA] INITIAL_STATE: ${this.currentState}`);
    
    // Start state evaluation every 1 second
    this._evaluationInterval = setInterval(() => {
      this._evaluateState();
    }, 1000);
  }

  _evaluateState() {
    const signals = this.signalCapture.getSignals();
    const now = performance.now();
    const timeSinceLastChange = now - this.lastStateChangeTime;
    
    // Enforce minimum cooldown
    if (timeSinceLastChange < this.cooldowns.minimum) {
      return; // Too soon to change state
    }
    
    // Determine new state using deterministic rules
    const newState = this._determineState(signals, now);
    
    // State transition
    if (newState !== this.currentState) {
      this._transitionTo(newState, signals);
    }
  }

  _determineState(signals, now) {
    // Priority 1: AWAY (overrides all)
    if (!signals.tab_visible) {
      this._resetDeepFocusCandidate();
      return CognitiveState.AWAY;
    }
    
    // Priority 2: DISTRACTED (window lost focus)
    if (!signals.panel_focused) {
      this._resetDeepFocusCandidate();
      return CognitiveState.DISTRACTED;
    }
    
    // Priority 3: IDLE (extended inactivity)
    if (signals.inactivity_ms > 30000) { // 30 seconds
      this._resetDeepFocusCandidate();
      return CognitiveState.IDLE;
    }
    
    // Priority 4: OFF_TASK (anxiety/frustration indicators)
    // Rapid clicking OR very high mouse velocity suggests off-task behavior
    if (signals.rapid_click_count >= 3 || signals.mouse_velocity > 2500) {
      this._resetDeepFocusCandidate();
      return CognitiveState.OFF_TASK;
    }
    
    // Priority 5: DEEP_FOCUS (sustained conditions required)
    // Requires: dwell time > 60s, low mouse velocity, low inactivity, stable behavior
    if (
      signals.dwell_time_ms > 60000 &&
      signals.mouse_velocity < 300 &&
      signals.inactivity_ms < 10000 &&
      signals.rapid_click_count === 0
    ) {
      // Track candidate for DEEP_FOCUS entry
      if (!this._deepFocusCandidate) {
        this._deepFocusCandidate = true;
        this._deepFocusCandidateTime = now;
      } else {
        // Check if sustained conditions met cooldown
        const candidateDuration = now - this._deepFocusCandidateTime;
        if (candidateDuration >= this.cooldowns.deepFocusEntry) {
          return CognitiveState.DEEP_FOCUS;
        }
      }
    } else {
      this._resetDeepFocusCandidate();
    }
    
    // Priority 6: THINKING (minimal movement, contemplative)
    // Very low mouse velocity AND minimal scrolling AND low inactivity
    if (
      signals.mouse_velocity < 200 &&
      signals.inactivity_ms < 5000 &&
      signals.inactivity_ms > 1000 && // Some pause, not constant movement
      signals.rapid_click_count === 0
    ) {
      return CognitiveState.THINKING;
    }
    
    // Default: ON_TASK (active engagement)
    return CognitiveState.ON_TASK;
  }

  _resetDeepFocusCandidate() {
    this._deepFocusCandidate = false;
    this._deepFocusCandidateTime = null;
  }

  _transitionTo(newState, signals) {
    const now = performance.now();
    const previousState = this.currentState;
    const stateDuration = now - this.stateEntryTime;
    
    // Determine transition reason
    const reason = this._getTransitionReason(newState, signals);
    
    // Log transition
    const transition = {
      timestamp: new Date().toISOString(),
      from_state: previousState,
      to_state: newState,
      reason: reason,
      previous_duration_ms: Math.round(stateDuration),
      signals_snapshot: {
        mouse_velocity: signals.mouse_velocity,
        scroll_depth: signals.scroll_depth,
        inactivity_ms: signals.inactivity_ms,
        rapid_click_count: signals.rapid_click_count,
        tab_visible: signals.tab_visible,
        panel_focused: signals.panel_focused,
        dwell_time_ms: signals.dwell_time_ms
      }
    };
    
    this.transitionLog.push(transition);
    
    // Console logging
    console.log(
      `[PRANA] STATE_CHANGE: ${previousState} → ${newState} | reason: ${reason} | duration: ${Math.round(stateDuration / 1000)}s`
    );
    
    // Update state
    this.currentState = newState;
    this.stateEntryTime = now;
    this.lastStateChangeTime = now;
  }

  _getTransitionReason(newState, signals) {
    switch (newState) {
      case CognitiveState.AWAY:
        return 'tab not visible';
      
      case CognitiveState.DISTRACTED:
        return 'window lost focus';
      
      case CognitiveState.IDLE:
        return `inactivity > 30s (${Math.round(signals.inactivity_ms / 1000)}s)`;
      
      case CognitiveState.OFF_TASK:
        if (signals.rapid_click_count >= 3) {
          return `rapid clicks detected (${signals.rapid_click_count})`;
        }
        return `high mouse velocity (${signals.mouse_velocity} px/s)`;
      
      case CognitiveState.DEEP_FOCUS:
        return `sustained focus (dwell: ${Math.round(signals.dwell_time_ms / 1000)}s, calm behavior)`;
      
      case CognitiveState.THINKING:
        return 'contemplative pause detected';
      
      case CognitiveState.ON_TASK:
        return 'active engagement';
      
      default:
        return 'state rule matched';
    }
  }

  // Public API

  /**
   * Get current cognitive state
   * @returns {string} Current state (one of CognitiveState values)
   */
  getCurrentState() {
    return this.currentState;
  }

  /**
   * Get duration in current state
   * @returns {number} Milliseconds in current state
   */
  getStateDuration() {
    return Math.round(performance.now() - this.stateEntryTime);
  }

  /**
   * Get complete state transition log
   * @returns {Array} Array of transition objects
   */
  getTransitionLog() {
    return [...this.transitionLog];
  }

  /**
   * Get current state summary
   * @returns {Object} State summary with duration
   */
  getStateSummary() {
    return {
      current_state: this.currentState,
      duration_ms: this.getStateDuration(),
      duration_seconds: Math.round(this.getStateDuration() / 1000),
      entry_time: new Date(Date.now() - this.getStateDuration()).toISOString(),
      total_transitions: this.transitionLog.length
    };
  }

  /**
   * Cleanup and stop engine
   */
  destroy() {
    if (this._evaluationInterval) {
      clearInterval(this._evaluationInterval);
      console.log('[PRANA] State Engine stopped');
    }
  }
}

// Module state
let stateEngineInstance = null;

/**
 * Initialize PRANA State Engine with signal capture instance
 * @param {Object} signalCapture - SignalCapture instance from signals.js
 * @returns {PranaCognitiveStateEngine} State engine instance
 */
export function initStateEngine(signalCapture) {
  if (!stateEngineInstance) {
    stateEngineInstance = new PranaCognitiveStateEngine(signalCapture);
  }
  return stateEngineInstance;
}

/**
 * Get active state engine instance
 * @returns {PranaCognitiveStateEngine|null} State engine instance or null
 */
export function getStateEngine() {
  return stateEngineInstance;
}

export default PranaCognitiveStateEngine;
