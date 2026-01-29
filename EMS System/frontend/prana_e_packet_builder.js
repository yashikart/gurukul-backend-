// prana_e_packet_builder.js
// Converts raw EMS browser signals into deterministic PRANA-E packets
// and forwards them to the BHIV Bucket via BucketBridge.

(function () {
  // Kill switch: set window.PRANA_DISABLED = true to disable all PRANA telemetry
  if (window.PRANA_DISABLED === true) {
    console.log('[PRANA-E] PRANA telemetry disabled via kill switch');
    return;
  }

  const PACKET_INTERVAL_MS = 5000; // 5-second windows

  if (!window.EMSSignals) {
    console.warn('[PRANA-E] EMSSignals not found on window. Telemetry builder idle.');
    return;
  }

  // Rolling window accumulators (per 5-second interval)
  let windowStartTs = Date.now();
  let agg = resetAggregates(windowStartTs);

  function resetAggregates(startTs) {
    return {
      startTs,
      endTs: startTs,
      // Aggregate simple counts (per window)
      keystroke_count: 0,
      mouse_events: 0,
      scroll_events: 0,
      content_clicks: 0,
      app_switches: 0,
      // Last seen global counters (for delta computation)
      _last_keystroke_count: 0,
      _last_mouse_events: 0,
      _last_scroll_events: 0,
      _last_content_clicks: 0,
      _last_app_switches: 0,
      // Track extremes
      max_idle_seconds: 0,
      last_snapshot: null,
    };
  }

  // Sample EMSSignals once per second and update aggregates
  setInterval(() => {
    const now = Date.now();
    const snapshot = window.EMSSignals.getState();
    agg.endTs = now;
    agg.last_snapshot = snapshot;

    // EMSSignals exposes monotonic counters; use per-window deltas
    const keys = snapshot.keystroke_count || 0;
    const prevKeys = agg._last_keystroke_count || 0;
    const deltaKeys = Math.max(0, keys - prevKeys);
    agg.keystroke_count += deltaKeys;
    agg._last_keystroke_count = keys;

    const mouse = snapshot.mouse_events || 0;
    const prevMouse = agg._last_mouse_events || 0;
    const deltaMouse = Math.max(0, mouse - prevMouse);
    agg.mouse_events += deltaMouse;
    agg._last_mouse_events = mouse;

    const scroll = snapshot.scroll_events || 0;
    const prevScroll = agg._last_scroll_events || 0;
    const deltaScroll = Math.max(0, scroll - prevScroll);
    agg.scroll_events += deltaScroll;
    agg._last_scroll_events = scroll;

    const clicks = snapshot.content_clicks || 0;
    const prevClicks = agg._last_content_clicks || 0;
    const deltaClicks = Math.max(0, clicks - prevClicks);
    agg.content_clicks += deltaClicks;
    agg._last_content_clicks = clicks;

    // app_switches is monotonic in EMSSignals; we want delta per window
    const switches = snapshot.app_switches || 0;
    const prevSwitches = agg._last_app_switches || 0;
    const deltaSwitches = Math.max(0, switches - prevSwitches);
    agg.app_switches += deltaSwitches;
    agg._last_app_switches = switches;

    const idle = snapshot.idle_seconds || 0;
    if (idle > agg.max_idle_seconds) {
      agg.max_idle_seconds = idle;
    }
  }, 1000);

  // Emit packet every 5 seconds
  setInterval(() => {
    if (!agg.last_snapshot) {
      return;
    }

    const snapshot = agg.last_snapshot;
    const windowDurationSeconds = Math.round((agg.endTs - agg.startTs) / 1000) || 5;

    const state = classifyState(snapshot, agg);
    const integrity_score = computeIntegrityScore(state, agg);

    const { active_seconds, idle_seconds, away_seconds } = deriveDurations(state, windowDurationSeconds);

    const context = getContext();

    const packet = {
      employee_id: context.employeeId,
      task_id: context.taskId,
      timestamp: new Date(agg.endTs).toISOString(),
      state,
      active_seconds,
      idle_seconds,
      away_seconds,
      integrity_score,
      raw_signals: {
        window_focus: !!snapshot.window_focus,
        browser_visibility: snapshot.browser_visibility,
        task_tab_active: !!snapshot.task_tab_active,
        idle_seconds: snapshot.idle_seconds,
        // Expose window-level max idle so integrity_score is fully recomputable from the packet
        max_idle_seconds: agg.max_idle_seconds,
        keystroke_count: agg.keystroke_count,
        mouse_events: agg.mouse_events,
        scroll_events: agg.scroll_events,
        content_clicks: agg.content_clicks,
        app_switches: agg.app_switches,
        browser_hidden: !!snapshot.browser_hidden,
        role: context.role,
        school_id: context.schoolId,
      },
    };

    if (window.BucketBridge && typeof window.BucketBridge.sendPacket === 'function') {
      window.BucketBridge.sendPacket(packet);
    } else {
      console.log('[PRANA-E] Built packet (BucketBridge not configured):', packet);
    }

    windowStartTs = Date.now();
    agg = resetAggregates(windowStartTs);
  }, PACKET_INTERVAL_MS);

  function classifyState(snapshot, aggregates) {
    const window_focus = !!snapshot.window_focus;
    const browser_visibility = snapshot.browser_visibility || 'visible';
    const task_tab_active = !!snapshot.task_tab_active;
    const idle_seconds = snapshot.idle_seconds || 0;

    // Derived activity buckets for clearer reasoning
    const hasKeystrokes = (aggregates.keystroke_count || 0) > 0;
    const hasMouse = (aggregates.mouse_events || 0) > 0;
    const hasScroll = (aggregates.scroll_events || 0) > 0;
    const hasContentClicks = (aggregates.content_clicks || 0) > 0;

    const totalActivity =
      (aggregates.keystroke_count || 0) +
      (aggregates.mouse_events || 0) +
      (aggregates.scroll_events || 0) +
      (aggregates.content_clicks || 0);

    const app_switches = aggregates.app_switches || 0;

    // AWAY: (window not focused OR browser hidden) AND idle >= 60
    if ((window_focus === false || browser_visibility === 'hidden') && idle_seconds >= 60) {
      return 'AWAY';
    }

    // FAKING
    if (
      window_focus === true &&
      browser_visibility === 'visible' &&
      idle_seconds >= 30 &&
      (aggregates.keystroke_count || 0) === 0 &&
      (aggregates.mouse_events || 0) <= 1 &&
      (aggregates.scroll_events || 0) === 0
    ) {
      return 'FAKING';
    }

    // WORKING
    // To qualify as WORKING we require *meaningful* interaction:
    //  - focused, visible, low idle
    //  - the EMS task tab is actually active
    //  - AND at least one of: keystrokes, scroll, content clicks
    // This prevents cheap mouse-jiggler macros from being counted as honest work.
    if (
      window_focus === true &&
      browser_visibility === 'visible' &&
      task_tab_active === true &&
      idle_seconds < 10 &&
      (hasKeystrokes || hasScroll || hasContentClicks)
    ) {
      return 'WORKING';
    }

    // DISTRACTED
    if (
      window_focus === true &&
      browser_visibility === 'visible' &&
      task_tab_active === false &&
      app_switches > 0
    ) {
      return 'DISTRACTED';
    }

    // IDLE
    if (
      window_focus === true &&
      browser_visibility === 'visible' &&
      idle_seconds >= 10 &&
      idle_seconds < 60
    ) {
      return 'IDLE';
    }

    // Default fallback
    return 'IDLE';
  }

  function computeIntegrityScore(state, aggregates) {
    let score = 1.0;
    const idle = aggregates.max_idle_seconds || 0;
    const app_switches = aggregates.app_switches || 0;

    const hasMouse = (aggregates.mouse_events || 0) > 0;
    const hasKeys = (aggregates.keystroke_count || 0) > 0;
    const hasScrollOrClicks =
      (aggregates.scroll_events || 0) > 0 || (aggregates.content_clicks || 0) > 0;

    if (idle > 20) {
      score -= 0.2;
    }

    if (app_switches > 3) {
      score -= 0.2;
    }

    if (hasMouse && !hasKeys && !hasScrollOrClicks) {
      score -= 0.1;
    }

    if (state === 'FAKING') {
      score -= 0.4;
    }

    if (state === 'AWAY') {
      score -= 0.5;
    }

    if (score < 0) score = 0;
    if (score > 1) score = 1;
    return Number(score.toFixed(2));
  }

  function deriveDurations(state, windowSeconds) {
    const clamped = Math.min(windowSeconds, 10); // enforce API upper bound
  
    switch (state) {
      case 'WORKING':
        return { active_seconds: clamped, idle_seconds: 0, away_seconds: 0 };
      case 'AWAY':
        return { active_seconds: 0, idle_seconds: 0, away_seconds: clamped };
      case 'IDLE':
      case 'DISTRACTED':
      case 'FAKING':
      default:
        return { active_seconds: 0, idle_seconds: clamped, away_seconds: 0 };
    }
  }

  function getContext() {
    const userCtx = window.EMSUserContext || null;
    const taskCtx = window.EMSTaskContext || null;

    return {
      employeeId: userCtx?.id ?? 'unknown',
      role: userCtx?.role ?? null,
      schoolId: userCtx?.school_id ?? null,
      taskId:
        (typeof taskCtx?.getCurrentTaskId === 'function'
          ? taskCtx.getCurrentTaskId()
          : taskCtx?.currentTaskId) ?? null,
    };
  }

  window.PRANAE = {
    // Expose helpers for manual debugging if needed
    classifyState,
    computeIntegrityScore,
  };
})();


