# Productization Work-Item Drafts

These files are the repository projection for the initial Last30days product
lanes and their productization-readiness gate. GitHub Issues are enabled on the
owned fork, and WI-000 through WI-009 were published and read back under their
stable idempotency markers. Creation and existing mapped-label application are
allowed; other issue and Project actions remain separately gated.

| Work item | GitHub issue |
|---|---|
| WI-000 | [#52](https://github.com/CochranResearchGroup/last30days-skill/issues/52) |
| WI-001 | [#54](https://github.com/CochranResearchGroup/last30days-skill/issues/54) |
| WI-002 | [#53](https://github.com/CochranResearchGroup/last30days-skill/issues/53) |
| WI-003 | [#57](https://github.com/CochranResearchGroup/last30days-skill/issues/57) |
| WI-004 | [#56](https://github.com/CochranResearchGroup/last30days-skill/issues/56) |
| WI-005 | [#58](https://github.com/CochranResearchGroup/last30days-skill/issues/58) |
| WI-006 | [#59](https://github.com/CochranResearchGroup/last30days-skill/issues/59) |
| WI-007 | [#61](https://github.com/CochranResearchGroup/last30days-skill/issues/61) |
| WI-008 | [#60](https://github.com/CochranResearchGroup/last30days-skill/issues/60) |
| WI-009 | [#55](https://github.com/CochranResearchGroup/last30days-skill/issues/55) |

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
