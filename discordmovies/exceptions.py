class Error(Exception):
    """
    Base class for other exceptions
    """
    pass


class MovieIdentityError(Error):
    """
    Raised when a movie cannot be identified from a link.
    """
    pass


class DiscordPermissionError(Error):
    """
    Raised when there is an issue regarding bot permissions with Discord.
    For example, if the bot doesn't have access to a channel that it needs
    to read.
    """
    pass

