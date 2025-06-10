class ServerException(Exception):
    """
    自定义服务器异常类，用于处理服务器端的错误
    """

    def __init__(self, status_code, message: str, details: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

    def __repr__(self):
        return f"ServerException(status_code={self.status_code}, message={self.args[0]}, details={self.details})"

    def __str__(self):
        return f"ServerException(status_code={self.status_code}, message={self.args[0]})"
