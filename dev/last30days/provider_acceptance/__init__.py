"""Provider-free acceptance harness for WI-010."""

from .campaign import execute, prepare, verify
from .catalog import default_catalog
from .contracts import (
    AcceptanceDependencies,
    AcceptanceReceipt,
    AcceptanceVerdict,
    CampaignSpec,
    EvidenceTier,
    ExecutionGrant,
)

__all__ = [
    "AcceptanceDependencies",
    "AcceptanceReceipt",
    "AcceptanceVerdict",
    "CampaignSpec",
    "EvidenceTier",
    "ExecutionGrant",
    "default_catalog",
    "execute",
    "prepare",
    "verify",
]
