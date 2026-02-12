# PRANA_IMPACT_DECLARATION_STANDARD.md

## 1. Purpose of Declaration
The PRANA Impact Declaration is a mandatory transparency mechanism for all BHIV product teams. Its purpose is to ensure that any interaction with the PRANA telemetry layer is explicitly disclosed, understood, and audited before changes are merged into production. This standard prevents silent coupling and maintains the "Observability vs. Control" boundary.

## 2. Mandatory Declaration Categories

### Category A: No PRANA Dependency
The feature or module does not ingest, query, or reference any PRANA states or signals. This is the default and desired state for most product features.

### Category B: Observational Read-Only
The module reads PRANA states for the sole purpose of non-reactive logging, audit trails, or population-level telemetry. No system outcome is modified based on the read data.

### Category C: Indirect Influence
PRANA data is used as a signal in a downstream system (e.g., Karma) which may indirectly influence visibility or non-critical feedback. Requires high-level description of the influence pathway.

### Category D: High-Risk Coupling
Any logic where PRANA state availability or value is a prerequisite for a system outcome (e.g., progression gate, access control). These declarations trigger an immediate Custodian Governance Review.

## 3. Boundary Definitions

- **Boundary Violation**: Any attempt to ingest semantic content (keystrokes, text) or PI into the PRANA stream.
- **Sovereignty Breach**: Exposing raw PRANA signals or derived states to a third-party service or uncurated database.
- **Outcome Contamination**: Using PRANA state (e.g., "Idle") to trigger mandatory system penalties or enforcement actions that lack a manual audit path.

## 4. Required Declaration Template

Teams must include this template in the header of their PR or Feature Spec:

```markdown
### [PRANA-IMPACT-DECLARATION]
- **Proposing Team**: [Team Name]
- **Target Product**: [e.g., Gurukul, WellnessBot]
- **Impact Category**: [A | B | C | D]
- **Involved Primitives**: [e.g., State.Reading, Signal.Aggregate_Scroll]
- **Outcome Pathway**: [Describe how data flows. If Category A, state "None"]
- **Non-Contamination Assertion**: "I certify this change does not turn observation into control." [Sign-off]
```

## 5. Examples

### Valid Declaration (Category B)
> "Adding student 'Focus State' to the Teacher Analytics aggregated report. No individual scores are generated; data is processed in batches of 50."

### Invalid Declaration (Category D - Rejected)
> "Using PRANA 'Distracted' state to pause the study timer and subtract learning points automatically."
> **Reason**: Turns observability into direct outcome enforcement without a buffer layer.

## 6. Review Trigger Rules
A **Custodian Review** is mandatory if:
1. Impact Category is **C** or **D**.
2. New dependencies are added to `PranaContext` or `bucket_consumer`.
3. The "Outcome Pathway" involves a real-time feedback loop to the user UI.
4. The change modifies the persistence or retention window of PRANA packets.
