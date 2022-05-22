import requests
from discordmovies.exceptions import MovieIdentityError
import json
from discordmovies.movies import Movie


class IMDB:
    """
    IMDB class that can get metadata for a film.
    """
    @staticmethod
    def get_imdb(content_id: int, omdb_api_key: str, movie: Movie):
        """
        Gets metadata from tmdb given an imdb link. Could
        technically work with a lot more than just imdb since it uses
        omdb.
        """

        find_r = requests.get(f"https://api.themoviedb.org/3/find"
                              f"/{content_id}?api_key={omdb_api_key}&"
                              f"language=en-US&external_source=imdb_id")

        if find_r.status_code == 404:
            raise MovieIdentityError(f"Could not find IMDB movie with "
                                     f"ID: {content_id}")
        if find_r.status_code != 200:
            raise ConnectionError("Something went wrong when trying to access "
                                  "TMDB. Here are the details about the "
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

        movie["Poster"] = image_base + image_size + content["poster_"
                                                            "path"]
        movie["Title"] = str(content["title"])
        movie["Genres"] = str(genres)
        movie["Runtime"] = str(content["runtime"])
        movie["Trailer"] = str(video)
        movie["User Score"] = str(content["vote_average"])
        movie["ID"] = "IMDB: " + str(content_id)
        movie["Release Date"] = str(content["release_date"]).split("-")[0]
