from discordmovies.movies import MovieList
from typing import List, Union


class DiscordMoviesAttributes(dict):
    """
    Variables in this class are shared between modules. This can be a huge pain
    when debugging because it can be difficult to know where something went
    wrong. However, it allows for some easier coding and better readability.
    """

    def __init__(self, name: str = "discordmovies",
                 movie_list: MovieList = None,
                 links: List[str] = None,
                 watched_links: List[str] = None,
                 attributes: List[str] = None,
                 exclude_attributes: List[str] = None,
                 bot: bool = None):

        super().__init__()

        if links is None:
            self["links"] = []

        if watched_links is None:
            self["watched_links"] = []

        if movie_list is None:
            self["movie_list"] = MovieList(
                categories=attributes, exclude_categories=exclude_attributes)
        else:
            self["movie_list"] = movie_list

        self["links"] = links
        self["name"] = name
        self["watched_links"] = watched_links
        self["bot"] = bot


class Keys(dict):
    """
    An object where various keys can be stored. Used to improve readability
    and simplify code.
    """

    def __init__(self, discord_auth_token: Union[str, int] = None,
                 tmdb_api_key: str = None):

        super().__init__()

        self["discord"] = discord_auth_token
        self["tmdb"] = tmdb_api_key


class DiscordAttributes(dict):
    """
    For storing various Discord related attributes. Used to improve code
    readability. Stores things such as channel ID, max_messages, and
    watched channel ID.
    """

    def __init__(self, channel_id: Union[str, int] = None,
                 watched_channel_id: Union[str, int] = None,
                 max_messages: int = None):

        super().__init__()

        self["channel_id"] = channel_id
        self["watched_channel_id"] = watched_channel_id
        self["max_messages"] = max_messages
