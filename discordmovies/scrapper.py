import requests
import json
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
        If metadata cannot be found, returns None.
        """

        site_info = Parser.identify(link)

        if site_info[1] is None:
            return [None, None, None, site_info[1]]

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
    def get_mal(content_id: int) -> list:
        """
        Take MAL link and return metadata for that entry.
        """
        import time

        # Rate limits yawn
        time.sleep(0.35)
        response = requests.get(f"https://api.jikan.moe/v4/anime/{content_id}")

        content = json.loads(response.content)["data"]

        genres = [i["name"] for i in content["genres"]]

        return [str(content["images"]["jpg"]["image_url"]),
                str([content["title_english"], content["title"]]),
                str(genres), str(content["duration"]),
                str(content["trailer"]["url"]),
                str(content["score"])]

    @staticmethod
    def get_imdb(content_id: int, omdb_api_key: str) -> list:
        """
        Gets metadata from imdb given a link. Uses omdbapi.com.
        """
        response = requests.get(f"https://api.themoviedb.org/3/find"
                                f"/{content_id}?api_key={omdb_api_key}&"
                                f"language=en-US&external_source=imdb_id")

        omdb_id = json.loads(response.content)["movie_results"][0]["id"]


        response = requests.get(f"https://api.themoviedb.org/3/movie"
                                f"/{omdb_id}?api_key={omdb_api_key}")

        content = json.loads(response.content)

        if content["genres"] is not None:
            genres = content["genres"].split(",")
        else:
            genres = content["genres"]

        return [str(content["image"]),
                str([content["fullTitle"], content["originalTitle"]]),
                str(genres), str(content["runtimeMins"]),
                str(content["trailer"]), str(content["imDbRating"])]
