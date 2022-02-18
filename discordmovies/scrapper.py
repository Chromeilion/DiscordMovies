import requests
import json

from discordmovies.exceptions import MovieIdentityError
from typing import Union
from discordmovies.parser import Parser


class Scrapper:
    """
    A class for handling scrapping from websites. Can get messages from a
    channel and extract media metadata from a supported link.
    """

    def __init__(self):
        self.auth = None
        self.bot = None
        self.headers = None

    def check_token(self):
        r = requests.get(f"https://discordapp.com/api/v9/users/@me",
                         headers=self.headers)
        if r.status_code == 401:
            raise ValueError("The discord token appears to be invalid. If you "
                             "are using a user token make sure --no-bot "
                             "is set.")

    def get_messages(self, channel_id: Union[int, str], auth: Union[int, str],
                     max_messages: int = 100, bot: bool = True) -> list:
        """
        Get all messages from a channel as a list of dictionaries.
        """

        if bot:
            self.headers = {
                "authorization": f"Bot {auth}",
            }
        else:
            self.headers = {
                "authorization": auth,
            }
        self.check_token()

        messages = []
        no_messages = 0
        before = None
        # Discord only lets us collect 100 messages at a time, so to get all
        # of them we need to send a couple requests.
        while no_messages < max_messages:
            if before:
                r = requests.get(f"https://discord.com/api/v9/channels/"
                                 f"{channel_id}/messages?limit=100&before"
                                 f"={before}",
                                 headers=self.headers)
            else:
                r = requests.get(f"https://discord.com/api/v9/channels/"
                                 f"{channel_id}/messages?limit=100",
                                 headers=self.headers)

            no_messages += 100
            result = json.loads(r.content)

            # When we reach the end of the channel we'll get no results
            # signaling a break
            if len(result) == 0:
                break

            before = result[-1]["id"]

            messages.append(result)

        return messages

    def get_metadata(self, link: str,
                     omdb_api_key: str = None) -> Union[list, None]:
        """
        Takes a link from a supported website and returns a list containing
        the metadata for the film/series.
        The list is in the order: [Image, Name, Genre, Length, Trailer, Score]
        If metadata cannot be found, raises MovieIdentityError.
        """

        site_info = Parser.identify(link)

        if site_info[1] is None:
            raise MovieIdentityError

        elif site_info[0] == "anilist.co":
            return self.get_anilist(site_info[1]) + [link]

        elif site_info[0] == "myanimelist.net":
            return self.get_mal(site_info[1]) + [link]

        elif site_info[0] in ["www.imdb.com", "m.imdb.com"]:
            if omdb_api_key is not None:
                return self.get_imdb(site_info[1],
                                     omdb_api_key=omdb_api_key) + [link]
            else:
                return None

    def get_anilist(self, content_id: int):
        """
        Get myanimelist id from anilist and pass it on to get_mal.
        """

        # Here we define our query as a multi-line string
        query = '''
        query ($id: Int) { 
        # (id)
          Media (id: $id, type: ANIME) { 
          # (id) (type: ANIME is hard-coded in the query)
            idMal
          }
        }
        '''

        # Define our query variables and values that will be used in the
        # query request
        variables = {
            'id': content_id
        }

        url = 'https://graphql.anilist.co'

        # Make the HTTP Api request
        response = requests.post(url,
                                 json={'query': query, 'variables': variables})

        if response.status_code != 200:
            # More work should be done here
            return None

        response_loaded = json.loads(response.content)

        return self.get_mal(response_loaded["data"]["Media"]["idMal"])

    @staticmethod
    def get_mal(content_id: int, sleep_time: float = 0.5) -> list:
        """
        Take MAL link and return metadata for that entry. Uses jikan.moe.
        """
        import time

        # Rate limits yawn
        time.sleep(sleep_time)
        response = requests.get(f"https://api.jikan.moe/v4/anime/{content_id}")
        sleep_time += 0.965

        while response.status_code == 429 and sleep_time < 24:
            # Try again in a bit in case of more severe rate limiting.
            sleep_time = sleep_time**2
            time.sleep(sleep_time)

            response = requests.get(f"https://api.jikan.moe/v4/anime/{content_id}")

        if response.status_code == 429:
            # This should theoretically never happen.
            raise ConnectionError("Jikan seems to be rate limiting more "
                                  "than it should. Try rerunning the "
                                  "program. If that doesn't fix it try "
                                  "again later.")
        elif response.status_code == 404:
            raise MovieIdentityError(f"Jikan returned a 404 not found error for movie with ID: {content_id}")
        elif response.status_code != 200:
            raise ConnectionError(f"Somethings wrong with Jikan. Specifically, it didn't return a 200 status code. "
                                  f"Here's some info about the response: \n "
                                  f"status code: {response.status_code} \n"
                                  f"response content: {response.content} \n"
                                  f"reason: {response.reason} \n"
                                  f"url: {response.url}")

        content = json.loads(response.content)["data"]

        genres = [i["name"] for i in content["genres"]]
        if len(genres) > 1:
            genres = ", ".join(genres)
        else:
            genres = genres[0]

        if content["title_english"] is None:
            title = content["title"]
        else:
            title = content["title_english"]

        return [content["images"]["jpg"]["image_url"],
                title,
                genres, str(content["duration"]),
                str(content["trailer"]["url"]),
                str(content["score"])]

    @staticmethod
    def get_imdb(content_id: int, omdb_api_key: str) -> list:
        """
        Gets metadata from tmdb given an imdb link. Could
        technically work with a lot more than just imdb.
        """

        find_r = requests.get(f"https://api.themoviedb.org/3/find"
                                f"/{content_id}?api_key={omdb_api_key}&"
                                f"language=en-US&external_source=imdb_id")

        if find_r.status_code == 404:
            raise MovieIdentityError(f"Could not find IMDB movie with ID: {content_id}")
        if find_r.status_code != 200:
            raise ConnectionError("Something went wrong when trying to access TMDB. Here are the details about the "
                                  "response:"
                                  f"status code: {find_r.status_code} \n"
                                  f"response content: {find_r.content} \n"
                                  f"reason: {find_r.reason} \n"
                                  f"url: {find_r.url}")

        omdb_id = json.loads(find_r.content)["movie_results"][0]["id"]


        lookup_r = requests.get(f"https://api.themoviedb.org/3/movie"
                                f"/{omdb_id}?api_key={omdb_api_key}")

        config_r = requests.get(f"https://api.themoviedb.org/3/configuration"
                                f"?api_key={omdb_api_key}")

        video_r = requests.get(f"https://api.themoviedb.org/3/movie/{omdb_id}"
                               f"/videos?api_key={omdb_api_key}")

        videos = json.loads(video_r.content)["results"]
        video = None
        for i in videos:
            if i["site"] == "YouTube":
                video = "https://youtu.be/" + i["key"]
                break

        content = json.loads(lookup_r.content)
        image_base = json.loads(config_r.content)["images"]["secure_base_url"]
        image_size = json.loads(config_r.content)["images"]["poster_sizes"][4]

        genres = [i["name"] for i in content["genres"]]
        if len(genres) > 1:
            genres = ", ".join(genres)
        else:
            genres = genres[0]

        return [image_base + image_size + content["poster_path"],
                content["title"],
                genres, str(content["runtime"]),
                video, str(content["vote_average"])]
