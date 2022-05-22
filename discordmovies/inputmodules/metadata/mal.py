import requests
import json
from discordmovies.exceptions import MovieIdentityError
from discordmovies.movies import Movie


class MAL:
    """
    MAL object that handles getting metadata from MAL.
    """
    @staticmethod
    def get_mal(movie: Movie, content_id: int, sleep_time: float = 0.5):
        """
        Take MAL link and fill metadata for that entry. Uses jikan.moe.
        """
        import time

        # Rate limits yawn
        time.sleep(sleep_time)
        response = requests.get(f"https://api.jikan.moe/v4/anime/{content_id}")
        sleep_time += 0.965

        while response.status_code == 429 and sleep_time < 24:
            # Try again in a bit in case of more severe rate limiting.
            sleep_time = sleep_time ** 2
            time.sleep(sleep_time)

            response = requests.get(f"https://api.jikan.moe/v4/"
                                    f"anime/{content_id}")

        if response.status_code == 429:
            # This should theoretically never happen.
            raise ConnectionError("Jikan seems to be rate limiting more "
                                  "than it should. Try rerunning the "
                                  "program. If that doesn't fix it try "
                                  "again later.")
        elif response.status_code == 404:
            raise MovieIdentityError(f"Jikan returned a 404 not found error "
                                     f"for movie with ID: {content_id}")
        elif response.status_code != 200:
            raise ConnectionError(f"Somethings wrong with Jikan. "
                                  f"Specifically, it didn't return a 200 "
                                  f"status code. "
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

        # Fill in all the attributes into the movie object.
        movie["Poster"] = content["images"]["jpg"]["image_url"]
        movie["Title"] = title
        movie["Genres"] = genres
        movie["Runtime"] = str(content["duration"])
        movie["Trailer"] = str(content["trailer"]["url"])
        movie["User Score"] = str(content["score"])
        movie["ID"] = "MAL: " + str(content_id)
        movie["Release Date"] = str(content["aired"]["prop"]["from"]["year"])
