class GptRateLimits:
    tokens_per_min: int = 200_000
    batch_queue: int = 2_000_000
    req_per_min: int = 500
