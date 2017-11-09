import typing


class PublicError(RuntimeError):
    category = None
    collection = None

    def __init__(self, message: str, category: typing.Optional[str] = None,
                 collection: typing.Optional[str] = None) -> None:
        super(RuntimeError, self).__init__(message)
        self.category = category
        self.collection = collection


class PublicWarning(RuntimeError):
    category = None
    collection = None

    def __init__(self, message: str, category: typing.Optional[str] = None,
                 collection: typing.Optional[str] = None) -> None:
        super(RuntimeError, self).__init__(message)
        self.category = category
        self.collection = collection


class RunError(RuntimeError):
    def __init__(self, message: str, errors: typing.List[Exception]) -> None:
        self._message = message
        super().__init__(message)
        self._errors = errors

    def __str__(self) -> str:
        return "{}: {}".format(self._message, self._errors)
