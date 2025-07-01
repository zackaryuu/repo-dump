class HabilException(Exception):
    pass

class HabilRequestException(HabilException):
    pass

class HabilRateLimitHalt(HabilRequestException):
    pass

class HabilRateLimitExceeded(HabilRequestException):
    pass