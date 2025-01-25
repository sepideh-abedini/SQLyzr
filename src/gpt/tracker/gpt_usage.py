from datetime import datetime, timedelta


class GptTokenUsage:
    tokens: int
    expires_at: datetime

    def __init__(self, tokens: int):
        self.tokens = tokens
        self.expires_at = datetime.utcnow() + timedelta(seconds=60)

    def expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    def expire(self):
        self.expires_at = datetime.utcnow()
