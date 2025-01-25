from datetime import datetime, timedelta


class GptTokenUsage:
    __tokens: int
    __expires_at: datetime

    def __init__(self, tokens: int):
        self.__tokens = tokens
        self.__expires_at = datetime.utcnow() + timedelta(seconds=60)

    @property
    def tokens(self):
        return self.__tokens

    def expired(self) -> bool:
        return datetime.utcnow() > self.__expires_at

    def expire(self):
        self.__expires_at = datetime.utcnow()
