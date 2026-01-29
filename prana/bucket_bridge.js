// Standalone copy of Gurukul's PRANA Bucket Bridge
// Source: Frontend/src/utils/bucket_bridge.js

class BucketBridge {
  constructor() {
    // Configuration
    this.BUCKET_ENDPOINT = '/bucket/prana/ingest'; // Will be prefixed with API_BASE_URL
    this.BATCH_SIZE = 5;                          // Send 5 packets at a time
    this.RETRY_DELAY = 2000;                      // 2 seconds between retries
    this.MAX_RETRIES = 3;                         // Max retry attempts
    
    // Queue for packets
    this.packetQueue = [];
    this.isSending = false;
    this.offlineQueue = []; // Temporary storage for offline handling
    
    // Stats
    this.sentCount = 0;
    this.failedCount = 0;
    
    console.log('[PRANA] Bucket Bridge initialized');
  }

  /**
   * Add a PRANA packet to the queue for sending
   * @param {Object} packet - PRANA packet to send
   */
  enqueuePacket(packet) {
    // Add timestamp when queued
    const queuedPacket = {
      ...packet,
      queued_at: new Date().toISOString()
    };
    
    this.packetQueue.push(queuedPacket);
    
    // Process queue if not already sending
    if (!this.isSending) {
      this.processQueue();
    }
  }

  /**
   * Process the packet queue in batches
   */
  async processQueue() {
    if (this.isSending || this.packetQueue.length === 0) {
      return;
    }

    this.isSending = true;
    
    try {
      // Process packets in batches
      while (this.packetQueue.length > 0) {
        // Get batch of packets
        const batch = this.packetQueue.splice(0, this.BATCH_SIZE);
        
        // Send batch
        await this.sendBatch(batch);
        
        // Small delay between batches to avoid overwhelming server
        await this.delay(100);
      }
    } catch (error) {
      console.error('[PRANA] Error processing packet queue:', error);
    } finally {
      this.isSending = false;
      
      // Process any new packets that arrived while sending
      if (this.packetQueue.length > 0) {
        setTimeout(() => this.processQueue(), 100);
      }
    }
  }

  /**
   * Send a batch of packets to the BHIV Bucket
   * @param {Array} batch - Array of PRANA packets to send
   */
  async sendBatch(batch) {
    let retries = 0;
    let success = false;
    
    while (retries < this.MAX_RETRIES && !success) {
      try {
        // Get API base URL from config
        const API_BASE_URL = await this.getApiBaseUrl();
        
        const response = await fetch(`${API_BASE_URL}${this.BUCKET_ENDPOINT}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-PRANA-BATCH-ID': `batch_${Date.now()}`,
            'X-CLIENT-TIMESTAMP': new Date().toISOString()
          },
          body: JSON.stringify({
            packets: batch,
            batch_size: batch.length,
            sent_at: new Date().toISOString()
          })
        });

        if (response.ok) {
          // Success - update stats and return
          this.sentCount += batch.length;
          console.log(`[PRANA] Batch of ${batch.length} packets sent successfully. Total sent: ${this.sentCount}`);
          success = true;
          
          // Log each packet in the batch
          batch.forEach(packet => {
            console.log(`[PRANA_SENT] ${packet.cognitive_state} | ${packet.focus_score} | ${packet.timestamp}`);
          });
        } else {
          // HTTP error - increment failed count and throw
          this.failedCount += batch.length;
          const errorText = await response.text();
          throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
      } catch (error) {
        retries++;
        
        if (retries >= this.MAX_RETRIES) {
          console.error(`[PRANA] Failed to send batch after ${this.MAX_RETRIES} retries:`, error.message);
          
          // Add failed packets back to queue for later retry
          this.offlineQueue.push(...batch);
          console.log(`[PRANA] Added ${batch.length} packets to offline queue. Offline queue size: ${this.offlineQueue.length}`);
        } else {
          console.warn(`[PRANA] Batch send failed, retry ${retries}/${this.MAX_RETRIES}:`, error.message);
          // Wait before retry
          await this.delay(this.RETRY_DELAY * retries); // Exponential backoff
        }
      }
    }
  }

  /**
   * Get API base URL from config
   */
  async getApiBaseUrl() {
    // Try to get from config file
    try {
      // Import dynamically to avoid circular dependencies
      const configModule = await import('../config.js');
      return configModule.default.API_BASE_URL || configModule.default;
    } catch (e) {
      // Fallback to environment variable or default
      return process.env.API_BASE_URL || 'http://localhost:8000/api/v1';
    }
  }

  /**
   * Handle network status changes
   */
  setupNetworkHandling() {
    // Handle online event
    window.addEventListener('online', () => {
      console.log('[PRANA] Network online, processing offline queue...');
      this.processOfflineQueue();
    });

    // Handle offline event
    window.addEventListener('offline', () => {
      console.log('[PRANA] Network offline, queuing packets for later...');
    });
  }

  /**
   * Process offline queue when network is available
   */
  async processOfflineQueue() {
    if (this.offlineQueue.length === 0) return;
    
    console.log(`[PRANA] Processing ${this.offlineQueue.length} packets from offline queue...`);
    
    // Move offline queue to main queue
    this.packetQueue.unshift(...this.offlineQueue);
    this.offlineQueue = [];
    
    // Process the queue
    if (!this.isSending) {
      this.processQueue();
    }
  }

  /**
   * Get bridge statistics
   */
  getStats() {
    return {
      sent: this.sentCount,
      failed: this.failedCount,
      queued: this.packetQueue.length,
      offline: this.offlineQueue.length,
      totalProcessed: this.sentCount + this.failedCount
    };
  }

  /**
   * Utility: Delay function
   */
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Initialize the bridge
   */
  async init() {
    this.setupNetworkHandling();
    console.log('[PRANA] Bucket Bridge fully initialized');
    
    // Process offline queue periodically
    setInterval(() => {
      if (navigator.onLine && this.offlineQueue.length > 0) {
        this.processOfflineQueue();
      }
    }, 10000); // Check every 10 seconds
  }
}

// Singleton instance
let bucketBridgeInstance = null;

/**
 * Initialize the Bucket Bridge
 * @returns {BucketBridge} The bucket bridge instance
 */
export async function initBucketBridge() {
  if (!bucketBridgeInstance) {
    bucketBridgeInstance = new BucketBridge();
    await bucketBridgeInstance.init();
  }
  return bucketBridgeInstance;
}

/**
 * Get the active bucket bridge instance
 * @returns {BucketBridge|null} The bucket bridge instance or null
 */
export function getBucketBridge() {
  return bucketBridgeInstance;
}

/**
 * Send a PRANA packet via the bucket bridge
 * @param {Object} packet - The PRANA packet to send
 */
export async function sendPranaPacket(packet) {
  const bridge = await getBucketBridge();
  if (bridge) {
    bridge.enqueuePacket(packet);
  } else {
    console.error('[PRANA] Bucket Bridge not initialized, cannot send packet');
  }
}

export default BucketBridge;


