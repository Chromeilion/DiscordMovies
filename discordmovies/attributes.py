from discordmovies.movies import MovieList
from typing import List


class DiscordMoviesAttributes:
    """
    Class that can be used for storing shared variables between classes.
    """

    def __init__(self, name: str = "discordmovies",
                 movie_list: MovieList = MovieList(),
                 links: List[str] = None,
                 watched_links: List[str] = None):

        self.movie_list = movie_list
        self.links = links
        self.name = name
        self.watched_links = watched_links
