from discordmovies.movies import MovieList
from typing import List


class DiscordMoviesAttributes:
    """
    Class that can be used for storing shared variables between classes.
    """

    def __init__(self, name: str = "discordmovies",
                 movie_list: MovieList = None,
                 links: List[str] = None,
                 watched_links: List[str] = None,
                 attributes: List[str] = None):

        if links is None:
            links = []

        if watched_links is None:
            watched_links = []

        if movie_list is None:
            if attributes is None:
                self.movie_list = MovieList()
            else:
                self.movie_list = MovieList(categories=attributes)

        self.links = links
        self.name = name
        self.watched_links = watched_links
