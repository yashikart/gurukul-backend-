# PRANA Backend Integration Notes

## EMS Backend Scope: Identity Provider Only

EMS backend provides **stable identifiers only**. PRANA consumes these identifiers to tag telemetry packets.

---

## ✅ What EMS Backend Provides

**User ID (`employee_id`)**
- Source: `users.id` from JWT token (`sub` claim)
- Frontend sets `window.EMSUserContext.id` on login
- Must remain stable across sessions

**Session ID (`session_id`)**
- Status: Not yet implemented
- Requirement: Generate on login, persist across refreshes
- Instead we are using JWT tokens for this

**Lesson ID (`task_id`)**
- Source: `lessons.id` (backend-issued Integer)
- Frontend should set `window.EMSTaskContext.currentTaskId` when viewing/editing lessons
- Must update correctly on lesson navigation

---

## ❌ What EMS Backend Does NOT Do

EMS backend does **NOT**:
- ❌ Interpret PRANA telemetry (no state analysis, no integrity scoring)
- ❌ Score PRANA data (no behavior evaluation, no karma calculation)
- ❌ Store PRANA packets (bucket endpoint is separate append-only ledger)
- ❌ Influence UX based on PRANA (no warnings, no restrictions, no metrics display)

**PRANA consumes identifiers only.** EMS backend provides stable IDs, nothing more.

---

## 🔌 Integration Flow

```
Login → JWT with user_id → window.EMSUserContext.id → PRANA employee_id
Lesson View → lesson.id → window.EMSTaskContext.currentTaskId → PRANA task_id
PRANA Packet → POST /bucket/prana/ingest → Validate & Store (no interpretation)
```

---

## 📋 Status

- ✅ User ID: Stable via JWT
- ✅ Lesson ID: Backend-issued, available via API
- ✅ Bucket endpoint: `/bucket/prana/ingest` working
- ⚠️ Session ID: To be implemented
- ⚠️ Task context: Frontend should auto-set `window.EMSTaskContext`

---

**Last Updated**: 2024 | **Maintained By**: EMS Backend Team (Yashika)

