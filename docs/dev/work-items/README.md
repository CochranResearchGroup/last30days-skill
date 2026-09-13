# Productization Work-Item Drafts

These files are the review surface for the initial Last30days product lanes.
They are not GitHub issues yet. Each contains a unique idempotency marker that
must be searched before any eventual create request.

## Proposed Dependency Graph

```text
WI-000 Productization program
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
