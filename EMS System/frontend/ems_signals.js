(function () {
    const SIGNAL_UPDATE_INTERVAL_MS = 1000;  // update in-memory state every 1s
    const SIGNAL_LOG_INTERVAL_MS = 5000;     // log summary every 5s
  
    const state = {
      // Time
      timestamp: new Date().toISOString(),
  
      // Focus / visibility
      window_focus: document.hasFocus(),
      browser_visibility: document.visibilityState || "visible",
  
      // Activity counts (per rolling 1s window)
      keystroke_count: 0,
      mouse_events: 0,
      mouse_distance: 0, // aggregate pixel distance in last window
      scroll_events: 0,
      content_clicks: 0,
  
      // Higher-level flags
      task_tab_active: document.hasFocus() && document.visibilityState === "visible",
      idle_seconds: 0,
  
      // Switch / background indicators
      app_switches: 0,
      browser_hidden: document.visibilityState === "hidden",
    };
  
    // Internal state (not exposed)
    let lastActivityTs = Date.now();
    let lastUpdateTs = Date.now();
    let lastMouseX = null;
    let lastMouseY = null;
  
    function markActivity() {
      lastActivityTs = Date.now();
    }
  
    // ---- Event Handlers ----
  
    // Window focus / blur
    window.addEventListener("focus", () => {
      state.window_focus = true;
      state.task_tab_active = state.window_focus && state.browser_visibility === "visible";
      console.log("[EMS] window_focus: true");
    });
  
    window.addEventListener("blur", () => {
      // Losing focus is treated as a potential app/tab switch
      state.window_focus = false;
      state.task_tab_active = false;
      state.app_switches += 1;
      console.log("[EMS] window_focus: false (possible app/tab switch)");
    });
  
    // Page visibility
    document.addEventListener("visibilitychange", () => {
      state.browser_visibility = document.visibilityState;
      state.browser_hidden = document.visibilityState === "hidden";
      state.task_tab_active = state.window_focus && state.browser_visibility === "visible";
  
      if (state.browser_hidden) {
        state.app_switches += 1; // conservative: any hide is treated as app/tab change
        console.log("[EMS] browser_visibility: hidden (tab backgrounded/minimized)");
      } else {
        console.log("[EMS] browser_visibility:", state.browser_visibility);
      }
    });
  
    // Keystrokes (rate only, no content)
    window.addEventListener(
      "keydown",
      () => {
        state.keystroke_count += 1;
        markActivity();
      },
      { passive: true }
    );
  
    // Mouse movement (events + approximate distance)
    window.addEventListener(
      "mousemove",
      (event) => {
        state.mouse_events += 1;
  
        if (lastMouseX !== null && lastMouseY !== null) {
          const dx = event.clientX - lastMouseX;
          const dy = event.clientY - lastMouseY;
          const distance = Math.sqrt(dx * dx + dy * dy);
          if (Number.isFinite(distance)) {
            state.mouse_distance += distance;
          }
        }
  
        lastMouseX = event.clientX;
        lastMouseY = event.clientY;
  
        markActivity();
      },
      { passive: true }
    );
  
    // Scroll
    window.addEventListener(
      "scroll",
      () => {
        state.scroll_events += 1;
        markActivity();
      },
      { passive: true }
    );
  
    // Content interaction (task-related clicks only)
    document.addEventListener(
      "click",
      (event) => {
        // Only count clicks on EMS task-relevant elements:
        // anything explicitly marked with data-ems-task or data-ems-interaction
        const target = event.target;
        const taskElement = target.closest?.(
          "[data-ems-task], [data-ems-interaction], [data-task-id]"
        );
  
        if (taskElement) {
          state.content_clicks += 1;
        }
  
        markActivity();
      },
      { passive: true, capture: true }
    );
  
    // ---- Periodic State Update ----
  
    function updateState() {
      const now = Date.now();
      state.timestamp = new Date(now).toISOString();
  
      // Idle time: seconds since last human input
      state.idle_seconds = Math.floor((now - lastActivityTs) / 1000);
  
      // Recompute derived flags
      state.window_focus = document.hasFocus();
      state.browser_visibility = document.visibilityState || state.browser_visibility;
      state.browser_hidden = state.browser_visibility === "hidden";
      state.task_tab_active = state.window_focus && state.browser_visibility === "visible";
  
      // Reset per-window counters every second (keeps counts bounded and inspectable)
      const elapsedSinceUpdate = now - lastUpdateTs;
      if (elapsedSinceUpdate >= SIGNAL_UPDATE_INTERVAL_MS) {
        state.keystroke_count = 0;
        state.mouse_events = 0;
        state.mouse_distance = 0;
        state.scroll_events = 0;
        state.content_clicks = 0;
        lastUpdateTs = now;
      }
    }
  
    setInterval(updateState, SIGNAL_UPDATE_INTERVAL_MS);
  
    // ---- Periodic Logging (for debugging / inspection) ----
  
    setInterval(() => {
      console.log("[EMS] Signal state:", {
        timestamp: state.timestamp,
        window_focus: state.window_focus,
        browser_visibility: state.browser_visibility,
        task_tab_active: state.task_tab_active,
        idle_seconds: state.idle_seconds,
        keystroke_count: state.keystroke_count,
        mouse_events: state.mouse_events,
        mouse_distance: Math.round(state.mouse_distance),
        scroll_events: state.scroll_events,
        content_clicks: state.content_clicks,
        app_switches: state.app_switches,
        browser_hidden: state.browser_hidden,
      });
    }, SIGNAL_LOG_INTERVAL_MS);
  
    window.EMSSignals = {

      getState() {
        return { ...state };
      },
    };
  })();