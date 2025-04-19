from dataclasses import dataclass


@dataclass(frozen=True)
class GptRateLimits:
    tokens_per_min: int
    batch_tokens_per_day: int
    req_per_min: int


TIER1_LIMITS = GptRateLimits(
    tokens_per_min=200_000,
    batch_tokens_per_day=2_000_000,
    req_per_min=400
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
