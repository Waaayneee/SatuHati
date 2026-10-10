"""Domain errors raised by services and tools. The API layer maps them to HTTP codes."""


class DomainError(Exception):
    def __init__(self, message: str, **details: object) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class NotFound(DomainError):
    pass


class PermissionDenied(DomainError):
    pass


class Conflict(DomainError):
    pass


class Refused(DomainError):
    """A safety rule refused the action (hard budget, opt-out, mission not active...)."""


class InvalidInput(DomainError):
    pass
