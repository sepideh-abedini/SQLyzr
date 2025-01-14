from dataclasses import dataclass


@dataclass
class GptRateLimits:
    tokens_per_min: int = 150_000
    batch_tokens_per_day: int = 1_500_000_000
    req_per_min: int = 500


TIER1_LIMITS = GptRateLimits(
    tokens_per_min=200_000,
    batch_tokens_per_day=2_000_000,
    req_per_min=500
)

TIER5_LIMITS = GptRateLimits(
    tokens_per_min=150_000_000,
    batch_tokens_per_day=1_500_000_000,
    req_per_min=10_000
)

LIMITS = {
    "tier1": TIER1_LIMITS,
    "tier5": TIER5_LIMITS
}
