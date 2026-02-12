# PRANA_SYSTEM_CANON.md

## A. What is the PRANA Canon?
The PRANA Canon is the authoritative and immutable definition of the PRANA system architecture and governance. It is the final source of truth for all system invariants.
- **Descriptors**: PRANA is *observational*, *non-invasive*, *ephemeral*, and *frozen*.
- **Versioning Philosophy**: PRANA does not follow semantic versioning for features. It follows a "Lock" model. The current version is **VERIFIED-LOCK-1**.
- **Truth Source**: The master files located in `Guardrails/PRANA_DOCS/` are the only authoritative references.

## B. System Dashboard (Conceptual — NOT UI)
This dashboard represents the internal monitoring checks required for system integrity. It must not be exposed to any user or administrator.

| Check                     | Expected State | Failure Condition                  |
| :------------------------ | :--------------| :--------------------------------- |
| **Invariants Intact?**    | YES            | Any mutation of core logic.        |
| **Boundary Breaches?**    | NONE           | Detection of semantic data ingest. |
| **State Mutation Events** | 0              | Any change to the state machine.   |
| **Governance Change Log** | LOCKED         | Unauthorized document edits.       |

**PROHIBITED DATA**: This dashboard must NEVER show user IDs, activity aggregates, success/failure scores, or engagement analytics.

## C. Daily State Recording Model
The system logs structural and governance events only to ensure long-term auditability.

**Allowed Records**:
- Checksum verification of core primitives.
- Timestamp of governance heartbeats.
- Log of formal boundary audits.

**Forbidden Records**:
- Behavioral data (e.g., "User stayed on page for X minutes").
- Performance metrics (e.g., "System processed X packets").
- Engagement data (e.g., "Feature X is popular").

## D. Governance Log Structure
All entries in the Governance Log must follow this format:
- `TIMESTAMP`: [ISO-8601]
- `EVENT_TYPE`: [INVARIANT_CHECK | BOUNDARY_AUDIT | CANON_AMENDMENT]
- `STATUS`: [PASS | FAIL | AMENDED]
- `VALIDATOR`: [CUSTODIAN_ID]
- `REMARKS`: [Neutral, structural observation only]
