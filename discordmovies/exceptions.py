class Error(Exception):
    """
    Base class for other exceptions
    """
    pass


class MovieIdentityError(Error):
    """
    Raised when a movie cannot be identified from a link.
    """
