class PublicError(RuntimeError):

    def __init__(self, message):
        super(RuntimeError, self).__init__(message)
