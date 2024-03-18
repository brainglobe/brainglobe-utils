class CommandLineInputError(Exception):
    """Exception raised for incorrect or illogical command line inputs that
    are not caught elsewhere.

    Attributes
    ----------
        message : str
            explanation of the error
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)
