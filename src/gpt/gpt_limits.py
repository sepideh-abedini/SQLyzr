class GptRateLimits:
    tokens_per_min: int = 150_000
    batch_tokens_per_day: int = 1_500_000_000
    req_per_min: int = 500
