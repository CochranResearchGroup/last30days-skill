# Productization Work-Item Drafts

These files are the review surface for the initial Last30days product lanes and
their productization-readiness gate.
GitHub Issues are enabled on the owned fork, but these drafts have not been
published as issues. The operator has now authorized WI-000 through WI-009
creation and application of existing mapped labels. Each file's unique
idempotency marker must be searched before creation and its resulting URL must
be read back before the repo claims remote identity.

## Proposed Dependency Graph

```text
WI-000 Productization program
├── WI-009 Productization readiness remediation
│   └── blocks new WI-001..WI-006 and WI-008 feature packets
├── WI-001 Isolated development runtime
│   ├── WI-004 X tailored follow
│   │   └── WI-005 Cross-service tailored follows
│   └── WI-007 Production hotfix path
├── WI-002 Search stored posts
│   ├── WI-003 Agent Q&A MCP
│   ├── WI-006 Saved monitors and digests ── depends also on WI-004
│   └── WI-008 Corpus quality evaluation
└── all lanes share governed schemas through coordinator review
```

The first recommended feature portfolio is WI-001, WI-002, and WI-004, with
the hotfix slot reserved by WI-007. WI-003 begins after WI-002 exposes the
evidence-preserving query contract. This keeps the WIP limit at three feature
lanes and minimizes shared-surface collisions.
