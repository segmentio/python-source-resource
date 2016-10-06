class PublicError(RuntimeError):

    def __init__(self, message):
        super(RuntimeError, self).__init__(message)


class RunError(RuntimeError):

    def __init__(self, message, errors):
        self._message = message
        super(RuntimeError, self).__init__(message)
        self._errors = errors

    def __str__(self):
        print("{}: {}", self._message, self._errors)
