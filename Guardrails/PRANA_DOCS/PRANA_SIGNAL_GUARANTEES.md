# PRANA Signal Guarantees

## Purpose

Explicit definition of PRANA's allowed signal surface, observability guarantees, and immutable boundaries that preserve PRANA sovereignty.

---

## 1. Allowed Signal Surface

### Permitted Signal Types

PRANA may only observe and emit the following signal categories:

- **Keyboard event counts** (aggregate, no content)
- **Mouse event counts** (aggregate, no position/trajectory)
- **Scroll event counts** (aggregate, no content context)
- **Focus event counts** (aggregate, no DOM inspection)
- **Route change events** (URL transitions only, no content)
- **Search query counts** (presence only, no query content)
- **Content display counts** (presence only, no content inspection)

### Signal Characteristics

- **Aggregate counts only** - No individual event details
- **Presence/absence only** - No semantic content
- **Temporal windows** - 2-second discrete windows
- **No cross-window correlation** - Ephemeral operation

---

## 2. Observability Guarantees

### What PRANA Provides

- **State telemetry** - Seven cognitive states (IDLE, ACTIVE, READING, TYPING, NAVIGATING, SEARCHING, VIEWING)
- **Signal aggregates** - Count-based signal presence indicators
- **Temporal markers** - ISO8601 timestamps per observation window
- **Deterministic mapping** - Same signals → Same state (no randomness)

### What PRANA Does Not Provide

- **Intent inference** - No user motivation or purpose
- **Behavior analysis** - No productivity or attention scoring
- **Content understanding** - No DOM, text, or media inspection
- **User identification** - No personal data beyond system_id
- **Historical correlation** - No cross-window state memory

---

## 3. Immutable Forbidden Signals

PRANA will **never** collect or infer:

### Interaction Privacy Violations
- ❌ **Keylogging** - No keystroke content capture
- ❌ **Mouse tracking** - No cursor position or movement patterns
- ❌ **User interaction sequences** - No gesture or click pattern analysis

### Content Inspection Violations
- ❌ **DOM inspection** - No HTML structure or content reading
- ❌ **Screenshot capture** - No visual state recording
- ❌ **Text content extraction** - No reading of user-generated content
- ❌ **Media content analysis** - No audio/video content inspection

### Behavioral Inference Violations
- ❌ **Attention scoring** - No focus or engagement metrics
- ❌ **Productivity metrics** - No work quality or output measurement
- ❌ **Intent detection** - No user goal or motivation inference
- ❌ **Misuse detection** - No policy violation or abuse identification

### Enforcement Violations
- ❌ **Action triggers** - No enforcement or intervention signals
- ❌ **Policy evaluation** - No relevance or compliance scoring
- ❌ **Decision outputs** - No binary flags or recommendations

---

## 4. Why PRANA Cannot Determine Relevance, Misuse, or Policy Outcomes

### Observational Limitation

PRANA operates at the **signal abstraction layer** only. It observes:
- **What signals are present** (counts)
- **When signals occur** (timestamps)
- **Signal patterns** (state transitions)

PRANA has **zero context** about:
- **Why signals occurred** (user intent)
- **What signals mean** (semantic interpretation)
- **Whether signals are appropriate** (policy compliance)

### Signal-to-Meaning Gap

**Signals are not behaviors:**
- Keyboard events ≠ productive work
- Scroll events ≠ comprehension
- Route changes ≠ intentional navigation

**States are not evaluations:**
- ACTIVE state ≠ relevance
- SEARCHING state ≠ misuse
- IDLE state ≠ policy violation

### Policy Evaluation Requires Context

Policy evaluation requires:
- **Domain knowledge** - What constitutes misuse in specific contexts
- **Historical patterns** - Cross-session and cross-user correlation
- **External data** - Legal frameworks, organizational policies, user agreements
- **Probabilistic reasoning** - Confidence thresholds and uncertainty handling

PRANA provides **none of these**. PRANA emits raw telemetry only.

### Enforcement Authority Separation

Enforcement requires:
- **Authorization** - Who can execute actions
- **Audit trails** - Who authorized what and when
- **Reversibility** - How to undo enforcement actions
- **Accountability** - Who is responsible for consequences

PRANA has **no authority** and **no accountability** for enforcement outcomes.

---

## 5. Trust, Privacy, and Sovereignty Rationale

### Trust Through Limitation

**PRANA is trusted because it is limited:**
- Cannot violate privacy (no content inspection)
- Cannot make mistakes (no decisions to make)
- Cannot be misused (no enforcement capabilities)
- Cannot be weaponized (no user-identifying content)

### Privacy Preservation

**Signal aggregation preserves privacy:**
- Counts reveal patterns, not content
- No personal information beyond system_id
- No cross-user correlation capability
- No persistent user profiles

**Ephemeral operation preserves privacy:**
- No state retention between windows
- No historical user behavior tracking
- No long-term pattern storage

### Sovereignty Through Isolation

**PRANA sovereignty is preserved by:**
- **No runtime coupling** - Independent operation from policy/enforcement systems
- **No bidirectional communication** - PRANA emits only, never receives commands
- **No configuration dependencies** - No external policy or rule loading
- **No shared state** - No database or cache dependencies

**PRANA cannot be coerced because:**
- It has no enforcement hooks
- It has no policy evaluation logic
- It has no user-facing features
- It has no control plane dependencies

---

## 6. No Runtime System Changes

### Documentation Scope

This document defines **architectural boundaries only**. It does not:
- Propose code changes
- Modify PRANA implementation
- Alter signal collection mechanisms
- Change state emission logic

### Contract Preservation

PRANA's existing contracts remain unchanged:
- **Bucket contract** - Unchanged transmission schema
- **State specification** - Unchanged state definitions
- **Failure matrix** - Unchanged fail-open behavior
- **Integration flow** - Unchanged telemetry emission

### Boundary Enforcement

These boundaries are enforced through:
- **Architecture review** - Design decisions must respect these boundaries
- **Code review** - Implementation must not violate these constraints
- **Testing** - Validation must confirm boundary compliance
- **Documentation** - Future teams must reference these guarantees

---

## Summary

PRANA is a **pure observational telemetry system** that:
- Emits signal aggregates and state telemetry only
- Never inspects content, tracks behavior, or evaluates policy
- Operates independently with no enforcement capabilities
- Preserves privacy through aggregation and ephemeral operation
- Maintains sovereignty through runtime isolation

These guarantees are **immutable** and form the foundation for safe post-PRANA intelligence layers.

