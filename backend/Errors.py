class EmptyFieldError(Exception):
    """Raised when a field is empty in request body"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
        
class InvalidFieldError(Exception):
    """Raised when a field is invalid in request body"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
        
class ResponseError(Exception):
    """Raised when a response is not as expected"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
        
class InvalidTokenError(Exception):
    """Raised when a token is invalid"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
        
class UnauthorizedError(Exception):
    """Raised when a user is not authorized to perform an action"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
        
class DuplicateFieldError(Exception):
    """Raised when a field is duplicated in request body"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
        
class MissingFieldError(Exception):
    """Raised when a field is missing in request body"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
        
class UserNotFoundError(Exception):
    """Raised when a user is not found"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
    