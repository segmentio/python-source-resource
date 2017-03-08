import typing

class PublicError(RuntimeError):
    def __init__(self, message: str) -> None:
        super(RuntimeError, self).__init__(message)

class PublicWarning(RuntimeError):
    def __init__(self, message: str) -> None:
        super(RuntimeError, self).__init__(message)

class RunError(RuntimeError):
    def __init__(self, message: str, errors: typing.List[Exception]) -> None:
        self._message = message
        super().__init__(message)
        self._errors = errors

    def __str__(self) -> str:
        return "{}: {}".format(self._message, self._errors)
