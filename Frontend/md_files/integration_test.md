## Test Scenarios

### 1. Normal Send Operations
**Scenario:** Happy path - packets sent successfully to bucket
- **Setup:** Online network, bucket endpoint available
- **Action:** Send PRANA packets via bucket bridge
- **Expected:** 
  - Packets batched (5 at a time)
  - Successful POST to `/bucket/prana/ingest`
  - Console logs show `[PRANA_SENT]` confirmation
  - Stats track sent count accurately

### 2. Network Offline Handling
**Scenario:** Network goes offline during operation
- **Setup:** Initially online, then simulate network disconnect
- **Action:** Continue sending packets while offline
- **Expected:**
  - Packets queued in offline queue
  - No errors thrown to UI
  - Queue size grows while offline
  - Console shows `[PRANA] Network offline` message

### 3. Retry Recovery
**Scenario:** Network comes back online after being offline
- **Setup:** Packets in offline queue due to network issues
- **Action:** Simulate network reconnect
- **Expected:**
  - Offline queue automatically processes
  - Packets sent in correct order
  - Queue empties successfully
  - Console shows `[PRANA] Network online` and processing message

### 4. Server Error Handling
**Scenario:** Bucket endpoint returns HTTP error
- **Setup:** Online network, but server returns 5xx error
- **Action:** Send packet to failing endpoint
- **Expected:**
  - Retries up to MAX_RETRIES (3)
  - Exponential backoff between retries
  - Failed packets moved to offline queue
  - Stats show failed count incremented

### 5. Order Preservation
**Scenario:** Multiple packets sent in sequence
- **Setup:** Continuous packet generation
- **Action:** Monitor packet ordering
- **Expected:**
  - Packets sent in chronological order
  - Batch processing maintains sequence
  - No reordering during retries

### 6. Batch Processing
**Scenario:** Multiple packets accumulate
- **Setup:** Rapid packet generation
- **Action:** Observe batching behavior
- **Expected:**
  - Groups of 5 packets sent together
  - Efficient network usage
  - Proper batch metadata included

## API Endpoints

### POST /bucket/prana/ingest
**Purpose:** Receive PRANA packets from frontend
**Headers:**
- `Content-Type: application/json`
- `X-PRANA-BATCH-ID: batch_timestamp`
- `X-CLIENT-TIMESTAMP: ISO8601`

**Payload:**
```json
{
  "packets": [...],
  "batch_size": 5,
  "sent_at": "ISO8601"
}
```

## Error Handling

### Network Errors
- Timeout: 30 seconds
- Retry: 3 attempts with exponential backoff
- Fallback: Queue for later delivery

### HTTP Errors
- 4xx: Client error, do not retry
- 5xx: Server error, retry with backoff
- Other: Treat as network error

## Performance Metrics

### Expected Throughput
- Batch size: 5 packets per request
- Frequency: Every 5 seconds (based on packet generation)
- Efficiency: Minimize network requests

### Memory Usage
- Queue size: Monitored and logged
- Memory cleanup: Processed packets removed
- Offline capacity: Temporary storage only

## Integration Points

### With PRANA Packet Builder
- Receives packets every 5 seconds
- Maintains loose coupling
- Zero impact on packet generation

### With Frontend UI
- No blocking operations
- Background processing
- Error isolation