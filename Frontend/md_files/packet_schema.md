# PRANA Packets

What gets sent every 5 seconds.

## Packet Structure

```javascript
{
  user_id,           
  session_id,        
  lesson_id,         
  timestamp,         
  cognitive_state,   
  active_seconds,    
  idle_seconds,      
  away_seconds,      
  focus_score,       
  raw_signals        
}
```

## Key Fields

### Context Fields (Currently null)
- **user_id** - From backend auth (not yet connected)
- **session_id** - From backend session (not yet connected)  
- **lesson_id** - From current page (not yet connected)

### Time Accounting (Always = 5.0 seconds)
- **active_seconds** - Learning time
- **idle_seconds** - No interaction time
- **away_seconds** - Tab hidden time

**Rule:** active + idle + away = exactly 5.0

### cognitive_state
Your current mental state (one of 7):
- ON_TASK, THINKING, IDLE, DISTRACTED, AWAY, OFF_TASK, DEEP_FOCUS

### focus_score (0-100)
Quality of attention:
- 95 = Deep focus, perfect
- 75 = On task, good
- 30 = Distracted
- 0 = Away/hidden tab

**How calculated:**
1. Base score from state
2. Penalties for anxiety/high velocity
3. Multiply by active time ratio

### raw_signals
All 8 behavior signals:
- dwell_time_ms
- hover_loops  
- rapid_click_count
- scroll_depth
- mouse_velocity
- inactivity_ms
- tab_visible
- panel_focused

## Example Packets

### Active Learning
```json
{
  "user_id": null,
  "session_id": null,
  "lesson_id": null,
  "timestamp": "2026-01-15T12:45:23.456Z",
  "cognitive_state": "ON_TASK",
  "active_seconds": 5.0,
  "idle_seconds": 0.0,
  "away_seconds": 0.0,
  "focus_score": 72,
  "raw_signals": {
    "dwell_time_ms": 145670,
    "scroll_depth": 45,
    "mouse_velocity": 650,
    "inactivity_ms": 890,
    "tab_visible": true,
    "panel_focused": true
  }
}
```

### Tab Switched Away
```json
{
  "cognitive_state": "AWAY",
  "active_seconds": 1.2,
  "away_seconds": 3.8,
  "focus_score": 18,
  "raw_signals": {
    "tab_visible": false,
    "inactivity_ms": 3800
  }
}
```

## Timing

**Emits:** Every 5 seconds exactly  
**Window:** Each packet = previous 5 seconds  
