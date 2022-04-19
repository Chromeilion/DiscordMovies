from discordmovies.attributes import DiscordMoviesAttributes
from typing import List, Dict
from discordmovies.movies import Movie


class Input:
    """
    Acts as a frontend for the input modules, providing a single object that
    can be used to access what you need.
    """

    def __init__(self, source_type: str, attributes: DiscordMoviesAttributes,
                 auth: str = None, bot: bool = None,
                 current_content: List[List[str]] = None,
                 tmdb_api_key: str = None, watched_channel_id: str = None,
                 remove_watched: bool = False, max_messages: int = 100,
                 movie_channel_id: str = None):
        self.source_type = source_type

        if self.source_type == "discord":
            from discordmovies.inputmodules.discord import Discord
            self.source = Discord(auth=auth, bot=bot, max_messages=max_messages)
        else:
            raise AttributeError("Source provided is not supported")

        self.messages = None
        self.attributes = attributes
        self.current_content = current_content
        self.tmdb_api_key = tmdb_api_key
        self.watched_channel_id = watched_channel_id
        self.remove_watched = remove_watched
        self.movie_channel_id = movie_channel_id

    def get_links(self, channel_id,
                  recalc: bool = False) -> List[Dict[str, str]]:
        """
        Get all movie links from the source, as well as other data.
        """

        if recalc or not self.messages:
            self.messages = self.source.get_links(channel_id=channel_id)
            return self.messages
        return self.messages

    def fill_movie_list(self, channel_id: str):
        [self.attributes.movie_list.append(Movie(values=i)) for i
         in self.get_links(channel_id=channel_id)]

    def fill_links(self, channel_id: str):
        links = self.get_links(channel_id=channel_id)
        self.attributes.links = [
            i["Link"] for i in links
        ]

    def remove_already_present(self):
        """
        Remove values from the movie list that are already present in
        current_content.
        """
        link_index = self.attributes.movie_list.get_cat_indexes()["Link"]
        current_links = [i[link_index] for i in self.current_content if i != []]

        self.attributes.movie_list.remove_by_attribute_value(
            attribute="Link",
            value=current_links)

    def mark_watched(self):
        links = self.get_links(channel_id=self.watched_channel_id, recalc=True)

        self.attributes.watched_links = [
            i["Link"] for i in links
        ]
        self.attributes.movie_list.mark_watched(
            watched_links=self.attributes.watched_links
        )

    def setup_movie_list(self):
        """
        Get values from a source that are not already present in
        current_content.
        """

        self.fill_movie_list(self.movie_channel_id)
        self.fill_links(self.movie_channel_id)
        # There may be links sent twice, these should be combined.
        self.attributes.movie_list.merge_duplicates(ignore=["Link"],
                                                    attribute="Link")

        if self.current_content:
            self.remove_already_present()

        self.attributes.movie_list.fill_all_metadata(
            tmdb_api_key=self.tmdb_api_key)

        self.attributes.movie_list.merge_duplicates()

        if self.watched_channel_id is not None:
            self.mark_watched()

        if self.remove_watched:
            self.attributes.movie_list.remove_by_attribute_value(
                attribute="Watched",
                value="True"
            )
