class ApiError(Exception):
    def __init__(self, error_message: str, status_code: int = None):
        self.error_message = error_message
        self.status_code = status_code
        super().__init__(self.error_message)

class AuthenticationError(ApiError):
    pass

class RateLimitError(ApiError):
    pass

class ValidationError(ApiError):
    pass 