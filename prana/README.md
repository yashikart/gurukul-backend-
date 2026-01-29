## PRANA Integration Bundle

This folder contains a **self-contained copy** of the core PRANA runtime used in Gurukul, so another frontend developer can integrate PRANA into their own web app without pulling the whole repo.

### Files

- `signals.js`  
  - Passive browser telemetry capture
  - Signals emitted (no content, no keylogging, no screenshots):
    - `dwell_time_ms`
    - `hover_loops`
    - `rapid_click_count`
    - `scroll_depth`
    - `mouse_velocity`
    - `inactivity_ms`
    - `tab_visible`
    - `panel_focused`
  - Auto-starts on import and logs `[PRANA-G SIGNALS]` every 5 seconds
  - Public API:
    - `initSignalCapture()` → returns singleton SignalCapture
    - `getSignalCapture()` → current singleton instance

- `prana_state_engine.js`  
  - Deterministic cognitive state machine driven **only** by signals
  - States:
    - `ON_TASK`, `THINKING`, `IDLE`, `DISTRACTED`, `AWAY`, `OFF_TASK`, `DEEP_FOCUS`
  - Enforces cooldowns, no flicker, priority rules
  - Public API:
    - `CognitiveState` enum
    - `initStateEngine(signalCapture)` → singleton engine
    - `getStateEngine()` → current engine

- `prana_packet_builder.js`  
  - Emits **one PRANA packet every 5 seconds**
  - Fields:
    - `user_id`, `session_id`, `lesson_id` (if available)
    - `timestamp`
    - `cognitive_state`
    - `active_seconds`, `idle_seconds`, `away_seconds` (sum = 5)
    - `focus_score` (0–100, deterministic)
    - `raw_signals` snapshot (same as `signals.js`)
  - **Important**: this standalone copy **does not call Karma directly** – it only builds packets. You can:
    - send them to your own backend
    - or pass them into the Bucket bridge / any other transport.
  - Public API:
    - `initPacketBuilder(signalCapture, stateEngine, contextProvider?)`
    - `getPacketBuilder()`

- `bucket_bridge.js`  
  - Generic queue + batch sender to a backend “Bucket” endpoint
  - Endpoint: `POST {API_BASE_URL}/bucket/prana/ingest`
  - Features:
    - Batching (`BATCH_SIZE = 5`)
    - Retries with backoff
    - Offline queue with re-send on reconnect
  - Public API:
    - `initBucketBridge()`
    - `getBucketBridge()`
    - `sendPranaPacket(packet)`

### Minimal Integration Steps (for another project)

1. **Copy this `prana` folder** into the other project.
2. In their main entry (e.g. `main.jsx` or `index.js`):

```js
import { initSignalCapture } from './prana/signals';
import { initStateEngine } from './prana/prana_state_engine';
import { initPacketBuilder } from './prana/prana_packet_builder';
import { initBucketBridge, sendPranaPacket } from './prana/bucket_bridge';

async function initPrana() {
  const signalCapture = initSignalCapture();
  const stateEngine = initStateEngine(signalCapture);

  // Optional: provide user/session/lesson context
  const contextProvider = {
    getContext() {
      return {
        user_id: null,      // fill from their auth system
        session_id: null,   // optional
        lesson_id: null,    // optional
      };
    },
  };

  const packetBuilder = initPacketBuilder(signalCapture, stateEngine, contextProvider);
  const bucket = await initBucketBridge();

  // Example: forward packets manually if needed
  // (in this copy, _emitPacket returns the packet; they can wire it into sendPranaPacket)
}

initPrana();
```

3. **Backend expectation for Bucket** (for their team):
   - Implement `POST /bucket/prana/ingest` that accepts:
   ```json
   {
     "packets": [ { ...prana_packet... }, ... ],
     "batch_size": 5,
     "sent_at": "2026-01-29T07:00:22.681Z"
   }
   ```

This is all you need to zip and send to another developer so they can integrate PRANA in their own frontend. No other files in this repo are required for the core PRANA runtime. 

## PRANA Integration Bundle

This folder contains everything another developer needs to integrate PRANA into their own web project.

The integration is split into four layers:

- `signals.js` – passive browser telemetry (mouse, scroll, visibility, focus, inactivity)
- `prana_state_engine.js` – deterministic cognitive state engine
- `prana_packet_builder.js` – 5-second PRANA packet emission
- `bucket_bridge.js` – single, queue-based exit to the Bucket

All modules are pure JavaScript and framework-agnostic. They assume a browser environment (DOM + `window`).

### Files

- `signals.js` – initializes a singleton `SignalCapture` and exposes:
  - `initSignalCapture()` – start capture and return instance
  - `getSignalCapture()` – get existing instance
- `prana_state_engine.js` – exposes:
  - `CognitiveState` – enum of states
  - `initStateEngine(signalCapture)` – create singleton state engine
  - `getStateEngine()` – access singleton
- `prana_packet_builder.js` – exposes:
  - `initPacketBuilder(signalCapture, stateEngine, contextProvider?)`
  - `getPacketBuilder()`
- `bucket_bridge.js` – exposes:
  - `initBucketBridge()`
  - `getBucketBridge()`
  - `sendPranaPacket(packet)`
- `state_transition_table.md` – spec for cognitive states and transitions
- `INTEGRATION_GUIDE.md` – step-by-step instructions for another developer


