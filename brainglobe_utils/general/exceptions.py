class CommandLineInputError(Exception):
    """Exception raised for incorrect or illogical command line inputs that
    are not caught elsewhere.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


class ArgumentError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
