class GptGatewayException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class GptRateLimitException(GptGatewayException):
    def __init__(self, msg=""):
        super().__init__("Token limit hit! " + msg)


class GptBatchNotCompletedException(GptGatewayException):
    def __init__(self):
        super().__init__("Batch not completed exception")


class GptBatchFailedException(GptGatewayException):
    def __init__(self, msg):
        super().__init__(msg)
