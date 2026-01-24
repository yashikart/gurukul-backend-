// bucket_bridge.js
// Responsible for sending PRANA-E packets to the BHIV Bucket endpoint.
// Pure frontend, uses fetch, no retries beyond what is defined here.

(function () {
  // Kill switch: set window.PRANA_DISABLED = true to disable all PRANA telemetry
  if (window.PRANA_DISABLED === true) {
    console.log('[PRANA-E][BucketBridge] PRANA telemetry disabled via kill switch');
    return;
  }

  const DEFAULT_ENDPOINT = 'http://localhost:8000/bucket/prana/ingest';

  let config = {
    endpoint: DEFAULT_ENDPOINT,
  };

  /**
   * Configure the bucket bridge.
   * @param {{ endpoint?: string }} options
   */
  function configure(options) {
    if (!options || typeof options !== 'object') return;
    if (typeof options.endpoint === 'string' && options.endpoint.trim() !== '') {
      config.endpoint = options.endpoint.trim();
    }
  }

  /**
   * Low-level POST helper with a single retry on failure.
   * Sends a **single** PRANA-E packet (API is per-packet, not batched).
   * @param {object} packet
   */
  async function postPacket(packet) {
    const body = JSON.stringify(packet);

    async function attempt(label) {
      try {
        const res = await fetch(config.endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body,
        });

        if (!res.ok) {
          console.error('[PRANA-E][BucketBridge]', label, 'HTTP error:', res.status, res.statusText);
          return false;
        }

        const data = await res.json().catch(() => null);
        console.log('[PRANA-E][BucketBridge]', label, 'success:', data);
        return true;
      } catch (err) {
        console.error('[PRANA-E][BucketBridge]', label, 'network error:', err);
        return false;
      }
    }

    const firstOk = await attempt('first-attempt');
    if (firstOk) return;

    // Single retry
    await attempt('retry-attempt');
  }

  /**
   * Public API: send a single PRANA-E packet.
   * @param {object} packet
   */
  function sendPacket(packet) {
    if (!packet || typeof packet !== 'object') {
      console.warn('[PRANA-E][BucketBridge] Ignoring invalid packet:', packet);
      return;
    }
    postPacket(packet);
  }

  window.BucketBridge = {
    configure,
    sendPacket,
  };
})();


