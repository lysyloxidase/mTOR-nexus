"""Pre-registered evidence tiers for graph edges."""

from enum import StrEnum


class Tier(StrEnum):
    """Strength of mechanistic evidence for an interaction."""

    ROBUST = "robust"
    PLAUSIBLE = "plausible"
    SPECULATIVE = "speculative"
