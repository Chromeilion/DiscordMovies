import requests
import json
from .mal import MAL
from discordmovies.movies import Movie


class Anilist:
    """
    Object for dealing with anilist. Used primarily to get metadata.
    """
    @staticmethod
    def get_anilist(content_id: int, movie: Movie):
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
            # More work should be done here for better error handling.
            return None

        response_loaded = json.loads(response.content)

        return MAL.get_mal(movie=movie,
                           content_id=response_loaded["data"]["Media"]["idMal"])
