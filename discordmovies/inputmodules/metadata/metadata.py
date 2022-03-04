from discordmovies.exceptions import MovieIdentityError
from urllib.parse import urlparse
from discordmovies.movies import Movie
from typing import Union
from .anilist import Anilist
from .imdb import IMDB
from .mal import MAL


class Metadata:
    """
    Class used to get metadata for Movies from various APIs.
    """

    @staticmethod
    def identify(link: str) -> tuple:
        """
        Takes a supported link and splits it into pieces. It analyzes it and
        returns the hostname and ID. If the website is not supported returns
        ID as None.
        """

        url_parsed = urlparse(link)
        path_split = url_parsed.path.split("/")
        content_id = None

        if url_parsed.hostname in ["anilist.co", "myanimelist.net"]:
            for i, j in enumerate(path_split):
                if j == "anime":
                    content_id = path_split[i+1]
                    break

        elif url_parsed.hostname in ["www.imdb.com", "m.imdb.com"]:
            for i, j in enumerate(path_split):
                if j == "title":
                    content_id = path_split[i+1]
                    break

        return url_parsed.hostname, content_id

    def get_metadata(self, movie: Movie,
                     omdb_api_key: str = None, ) -> Union[list, None]:
        """
        Takes a Movie object which has a link in it and adds as much metadata
        as it can to it, trying to fill in the other attributes.
        """

        site_info = self.identify(movie["Link"])

        if site_info[1] is None:
            raise MovieIdentityError

        elif site_info[0] == "anilist.co":
            return Anilist.get_anilist(content_id=site_info[1], movie=movie)

        elif site_info[0] == "myanimelist.net":
            return MAL.get_mal(content_id=site_info[1], movie=movie)

        elif site_info[0] in ["www.imdb.com", "m.imdb.com"]:
            if omdb_api_key is not None:
                return IMDB.get_imdb(
                    content_id=site_info[1],
                    omdb_api_key=omdb_api_key,
                    movie=movie
                )
            else:
                return None
