class SignalCapture {
  constructor() {
    // Signal state (raw captures only)
    this.signals = {
      dwell_time_ms: 0,
      hover_loops: 0,
      rapid_click_count: 0,
      scroll_depth: 0,
      mouse_velocity: 0,
      inactivity_ms: 0,
      tab_visible: true,
      panel_focused: true
    };

    // Internal tracking (not exposed)
    this._mousePositions = [];
    this._lastMouseTime = 0;
    this._lastActivityTime = performance.now();
    this._pageLoadTime = performance.now();
    this._clickTimestamps = [];
    this._lastScrollDepth = 0;
    this._hoverPositions = [];
    this._logInterval = null;

    this._init();
  }

  _init() {
    // Attach all listeners
    this._attachMouseListeners();
    this._attachScrollListeners();
    this._attachClickListeners();
    this._attachVisibilityListeners();
    this._attachFocusListeners();
    this._attachInactivityTracker();

    this._startLiveLogging();
  }

  _attachMouseListeners() {
    // Passive listener for mouse movement
    document.addEventListener('mousemove', (e) => {
      const now = performance.now();
      const pos = { x: e.clientX, y: e.clientY, time: now };

      // Calculate velocity
      if (this._mousePositions.length > 0) {
        const last = this._mousePositions[this._mousePositions.length - 1];
        const dx = pos.x - last.x;
        const dy = pos.y - last.y;
        const dt = now - last.time;
        
        if (dt > 0) {
          const distance = Math.sqrt(dx * dx + dy * dy);
          this.signals.mouse_velocity = Math.round(distance / dt * 1000); // px/s
        }
      }

      // Track hover loops (circular/repeated movements in same area)
      this._hoverPositions.push(pos);
      if (this._hoverPositions.length > 20) {
        this._hoverPositions.shift();
      }
      this._detectHoverLoops();

      // Keep last 10 positions for velocity smoothing
      this._mousePositions.push(pos);
      if (this._mousePositions.length > 10) {
        this._mousePositions.shift();
      }

      this._updateActivity();
    }, { passive: true });
  }

  _detectHoverLoops() {
    if (this._hoverPositions.length < 10) return;

    // Check if mouse is hovering in a small area (potential indecision)
    const recent = this._hoverPositions.slice(-10);
    const xs = recent.map(p => p.x);
    const ys = recent.map(p => p.y);
    
    const xRange = Math.max(...xs) - Math.min(...xs);
    const yRange = Math.max(...ys) - Math.min(...ys);
    
    // If confined to small area (50px box) for 10 movements = hover loop
    if (xRange < 50 && yRange < 50) {
      this.signals.hover_loops++;
    }
  }

  _attachScrollListeners() {
    document.addEventListener('scroll', () => {
      // Calculate scroll depth percentage
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      
      const maxScroll = documentHeight - windowHeight;
      if (maxScroll > 0) {
        this.signals.scroll_depth = Math.round((scrollTop / maxScroll) * 100);
      } else {
        this.signals.scroll_depth = 100;
      }

      this._updateActivity();
    }, { passive: true });
  }

  _attachClickListeners() {
    document.addEventListener('click', () => {
      const now = performance.now();
      
      // Track clicks for rapid click detection
      this._clickTimestamps.push(now);
      
      // Keep only clicks from last 2 seconds
      this._clickTimestamps = this._clickTimestamps.filter(t => now - t < 2000);
      
      // Rapid clicks = 3+ clicks within 2 seconds (anxiety/frustration)
      if (this._clickTimestamps.length >= 3) {
        this.signals.rapid_click_count = this._clickTimestamps.length;
      } else {
        this.signals.rapid_click_count = 0;
      }

      this._updateActivity();
    }, { passive: true });
  }

  _attachVisibilityListeners() {
    document.addEventListener('visibilitychange', () => {
      this.signals.tab_visible = !document.hidden;
      this._updateActivity();
    }, { passive: true });
  }

  _attachFocusListeners() {
    window.addEventListener('focus', () => {
      this.signals.panel_focused = true;
      this._updateActivity();
    }, { passive: true });

    window.addEventListener('blur', () => {
      this.signals.panel_focused = false;
    }, { passive: true });
  }

  _attachInactivityTracker() {
    // Check inactivity every 100ms
    setInterval(() => {
      const now = performance.now();
      this.signals.inactivity_ms = Math.round(now - this._lastActivityTime);
      
      // Update dwell time (only when visible and focused)
      if (this.signals.tab_visible && this.signals.panel_focused) {
        this.signals.dwell_time_ms = Math.round(now - this._pageLoadTime);
      }
    }, 100);
  }

  _updateActivity() {
    this._lastActivityTime = performance.now();
    this.signals.inactivity_ms = 0;
  }

  _startLiveLogging() {
    // Log current signals every 5 seconds
    this._logInterval = setInterval(() => {
      console.log('[PRANA-G SIGNALS]', {
        timestamp: new Date().toISOString(),
        mouse_velocity: this.signals.mouse_velocity,
        scroll_depth: this.signals.scroll_depth,
        inactivity_ms: this.signals.inactivity_ms,
        rapid_click_count: this.signals.rapid_click_count,
        tab_visible: this.signals.tab_visible,
        panel_focused: this.signals.panel_focused,
        dwell_time_ms: this.signals.dwell_time_ms,
        hover_loops: this.signals.hover_loops
      });
    }, 5000);
  }

  // Public method to get current signals (for future integration)
  getSignals() {
    return {
      ...this.signals,
      timestamp: new Date().toISOString()
    };
  }

  // Cleanup method
  destroy() {
    if (this._logInterval) {
      clearInterval(this._logInterval);
    }
  }
}

// Auto-initialize when module loads
let signalCaptureInstance = null;

export function initSignalCapture() {
  if (!signalCaptureInstance) {
    signalCaptureInstance = new SignalCapture();
    console.log('[PRANA-G] Signal Capture Layer initialized');
  }
  return signalCaptureInstance;
}

export function getSignalCapture() {
  return signalCaptureInstance;
}

// Auto-start if loaded in browser
if (typeof window !== 'undefined') {
  initSignalCapture();
}
