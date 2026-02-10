# PRANA Packet Invariants

## Purpose

What PRANA packets can prove, what they cannot prove, and what interpretations are forbidden. These invariants protect against misuse during replay, audit, or hostile analysis.

**Immutability and Safe-by-Design Guarantees:**
- Packet invariants are **immutable** - they cannot be relaxed, modified, or reinterpreted
- PRANA is **safe-by-design** - all failures result in fail-open behavior with zero application impact
- Packets are **non-authoritative** - they are observational telemetry only, never evidence, never enforceable, never behavioral
- All failure modes are **fail-open** - failures never block operation, never propagate unintended effects, never allow misuse

---

## Packet Structure

**Required fields:**
- `system_id` (UUID) - System identifier, not user identifier
- `timestamp` (ISO8601) - Observation window start time
- `state` - One of: IDLE, ACTIVE, READING, TYPING, NAVIGATING, SEARCHING, VIEWING
- `signals` - Aggregate counts only (keyboard, mouse, scroll, focus, route, search, content)
- `window_duration_ms` - Typically 2000ms
- `metadata` - PRANA version and window ID

**Guarantees:**
- Immutable once constructed (append-only)
- All fields required (missing fields → packet discarded)
- Schema-compliant (non-compliant → transmission fails)

---

## What Packets Contain

**Signals:** Aggregate counts only. No event content, sequences, or semantics. Individual events are discarded immediately after counting.

**States:** Observational classifications derived from signal patterns within a 2-second window. States are deterministic and reproducible: same signals → same state. States reflect signal patterns, not user truth, behavior, or intent.

**Timestamps:** Observation window start time, not individual event timing. Timestamps are observational only, never authoritative.

**System ID:** System instance identifier, not user identifier. Not personally identifiable information.

---

## What Packets Cannot Prove

Packets **never** prove:
- ❌ User activity (signals may be automated, system-generated, or non-user interactions)
- ❌ User intent or motivation (packets have zero context about user purpose or goals)
- ❌ User behavior patterns (packets observe signal counts, not behaviors)
- ❌ Event causality or timing (no proof of cause-and-effect or exact event timing)
- ❌ State accuracy (states are observational classifications that reflect signals, not user truth or reality)
- ❌ Packet authenticity or integrity (no cryptographic guarantees, no proof of origin or tampering)

**Packets are non-authoritative:** They are observations, not facts. They cannot be used as evidence, for judgment, or for enforcement. Packets are pure observational telemetry with zero behavioral, legal, or policy authority.

---

## State Classification Guarantees

**States are observational classifications only:**
- States are derived from signal patterns within a 2-second observation window
- States are deterministic: same signal patterns → same state classification
- States are reproducible: given the same signals, PRANA will always derive the same state
- States reflect signal patterns, not user truth, behavior, intent, or reality

**States are NOT:**
- ❌ Proof of user behavior or activity
- ❌ Proof of user intent or motivation
- ❌ Proof of user productivity or engagement
- ❌ Proof of policy compliance or violation
- ❌ Evaluations or judgments about user actions
- ❌ Truth or reality about user state

**State non-authority guarantee:** States are telemetry classifications, not behavioral facts. States cannot be used to prove user behavior, intent, productivity, compliance, or any other user-related claim.

---

## What This Does NOT Allow

**Intent inference:** Cannot infer user motivation, goals, decision-making, or purpose. Packets have zero context about user intent.

**Productivity inference:** Cannot infer work quality, effectiveness, performance, or output. Packets observe signals, not productivity.

**Causality claims:** Cannot claim cause-and-effect relationships between events, signals, states, or user actions. No causal inference is possible.

**Policy evaluation:** Cannot evaluate compliance, misuse, relevance, or appropriateness. Packets have zero policy context.

**Enforcement triggers:** Cannot trigger application changes, control operations, or system modifications. Packets are read-only telemetry.

**Behavioral analysis:** Cannot analyze, evaluate, or judge user behavior. Packets are observational only, not behavioral.

---

## Common Misinterpretations

**"Packets prove user activity"**  
Reality: Packets prove only that PRANA observed signals during a window. Signals may be automated, system-generated, or non-user interactions. Packets cannot prove user activity.

**"States prove user behavior"**  
Reality: States are observational classifications derived from signal patterns. States reflect signals, not user behavior, intent, or truth. States are telemetry, not behavioral facts.

**"States are accurate representations of user state"**  
Reality: States are observational classifications that reflect signal patterns, not user truth or reality. States cannot prove what the user is actually doing, thinking, or intending.

**"Timestamps prove event timing"**  
Reality: Timestamps reflect observation window start time, not individual event timing. Clock drift, network delays, and processing delays affect timestamps. Timestamps are observational only, never authoritative.

**"System ID identifies users"**  
Reality: System ID identifies system instances, not users. System ID is not personally identifiable information and cannot be used to identify, track, or correlate users.

**"Replay enables surveillance"**  
Reality: Replay enables read-only access to pre-aggregated telemetry values, not surveillance. Cannot prove past behavior, track users, or enable retroactive judgment.

**"Packets are audit logs"**  
Reality: Packets are telemetry, not audit logs. Packets lack cryptographic authenticity, integrity, and non-repudiation guarantees required for audit logs. Packets cannot be used as evidence.

---

## Failure Handling

### Construction Failures

**Failure conditions:** Missing fields, type errors, schema violations, signal aggregation failures, state derivation failures, metadata construction failures.

**Fail-open behavior:**
- Packet is immediately discarded
- No retry, no queue, no persistence
- No application impact
- No blocking or delay of application operations
- Silent operation cessation

**Failure non-authority:** Construction failures are operational events, not diagnostic events. Failures do not indicate system problems, user problems, policy violations, or security issues. Failures never propagate unintended effects.

### Transmission Failures

**Failure conditions:** Network errors, timeouts, authentication failures, rate limits, storage full, connection refused, DNS failure.

**Fail-open behavior:**
- Packet is immediately discarded after single attempt
- No retry, no backoff, no queue, no persistence
- No application impact
- No blocking or delay of application operations
- Silent operation cessation

**Failure non-authority:** Transmission failures are operational events, not diagnostic events. Failures do not indicate packet importance, system problems, user problems, or policy violations. Failures never propagate unintended effects.

### Fail-Open Guarantee

**All failures result in fail-open behavior:**
- Failures never block application operations
- Failures never delay application operations
- Failures never propagate unintended effects
- Failures never allow misuse or abuse
- Failures never impact system functionality
- Failures result in silent operation cessation only

**Fail-open is immutable:** This guarantee cannot be relaxed, modified, or reinterpreted. All failure modes must preserve fail-open behavior.

---

## Summary

PRANA packets are **pure observational telemetry** that:

**Contain:**
- Aggregate signal counts only (no event content, sequences, or semantics)
- Observational state classifications derived from signal patterns (not user truth or behavior)
- Observation window timestamps (not authoritative event timing)
- System instance identifiers (not user identifiers)

**Prove only:**
- That PRANA observed signals during a specific window
- That PRANA derived a state classification from those signals
- That PRANA constructed a packet with specific field values

**Cannot prove:**
- User activity, intent, behavior, or compliance
- Event causality, timing, or accuracy
- State accuracy (states reflect signals, not user truth)
- Packet authenticity or integrity

**Cannot be used for:**
- Surveillance, judgment, or enforcement
- Evidence, audit trails, or legal purposes
- Behavioral analysis or productivity evaluation
- Policy compliance evaluation or misuse detection

**Are non-authoritative:**
- Packets are observations, not facts
- Packets are telemetry, not evidence
- Packets are classifications, not truth
- Packets cannot be used as proof of anything beyond PRANA's observation

**Fail-open safely:**
- All failures result in silent operation cessation
- Zero application impact
- Zero blocking or delay
- Zero propagation of unintended effects
- Zero opportunity for misuse

These invariants are **immutable** and form the foundation for safe packet interpretation, replay, and analysis. These guarantees cannot be relaxed, modified, or reinterpreted.
