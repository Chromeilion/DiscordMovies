from discordmovies.parser import Parser
from typing import Union
from discordmovies.movies import Movie
from discordmovies.attributes import DiscordMoviesAttributes
from discordmovies.scrapper import Scrapper
from typing import List
from discordmovies.filemodules.filehelper import FileHelper


class DiscordMovies:
    """
    A class for going through a discord movie recommendations channel and
    extracting all links. These links can then be uploaded to Google Sheets
    or exported to a CSV.
    """

    def __init__(self, discord_auth_token: Union[str, int], bot: bool = True,
                 doc_name: str = "discordmovies", attributes: List[str] = None,
                 exclude_attributes: List[str] = None):
        self.scrapper = Scrapper()
        self.auth_token = discord_auth_token
        self.bot = bot
        self.attributes = DiscordMoviesAttributes(
            name=doc_name,
            attributes=attributes,
            exclude_attributes=exclude_attributes
        )

    def discord_to_file(self, filetype: str,
                        channel_id: Union[str, int],
                        watched_channel_id: Union[str, int] = None,
                        sheet_id: Union[str, int] = None,
                        max_messages: int = 100,
                        tmdb_api_key: str = None,
                        remove_watched: bool = False,
                        reformat_sheet: bool = False):
        """
        Extract all movies from a Discord channel and save them to a Google
        Sheet or CSV.
        """

        helper = FileHelper(filetype=filetype, attributes=self.attributes,
                            sheet_id=sheet_id, reformat_sheet=reformat_sheet)

        if helper.exists():

            current_content = helper.get_values()

            if current_content:
                if current_content[0] != self.attributes.movie_list.\
                        get_categories():
                    print("File formatting does not match current formatting "
                          "settings. Sheet will be completely rewritten.")
                    overwrite = True
                    current_content = []
                else:
                    overwrite = False
            else:
                overwrite = False

            if not self.attributes.movie_list:
                self.get_links(channel_id=channel_id,
                               watched_channel_id=watched_channel_id,
                               max_messages=max_messages,
                               tmdb_api_key=tmdb_api_key,
                               current_content=current_content,
                               remove_watched=remove_watched)
            helper.write_existing(overwrite=overwrite)
        else:
            if not self.attributes.movie_list:
                self.get_links(channel_id=channel_id,
                               watched_channel_id=watched_channel_id,
                               max_messages=max_messages,
                               tmdb_api_key=tmdb_api_key,
                               remove_watched=remove_watched)
            helper.write_new()

    def get_links(self, channel_id: Union[str, int],
                  watched_channel_id: Union[str, int] = None,
                  max_messages: int = 100,
                  tmdb_api_key: str = None,
                  current_content: list = None,
                  remove_watched: bool = False):
        """
        Gets messages and parses them, then it gets rid of duplicates and
        non-movie links, as well as movies already present in current_content.
        The output goes into self.content.
        """

        # Get all messages from channel
        movie_messages = self.scrapper.get_messages(
            channel_id=channel_id,
            auth=self.auth_token,
            max_messages=max_messages,
            bot=self.bot
        )

        # Extract all links from messages
        parser_out = Parser.extract_links(movie_messages)

        [self.attributes.movie_list.append(Movie(values=i)) for i in parser_out]

        self.attributes.links = [i['Link'] for i in parser_out]

        if current_content is not None:
            link_index = self.attributes.movie_list.get_cat_indexes()["Link"]
            current_links = [i[link_index] for i in current_content if i != []]

            self.attributes.movie_list.remove_by_attribute_value(
                attribute="Link",
                value=current_links)

        self.attributes.movie_list.fill_all_metadata(tmdb_api_key)
        self.attributes.movie_list.merge_duplicates()

        if watched_channel_id:
            watched_messages = self.scrapper.get_messages(
                channel_id=watched_channel_id,
                auth=self.auth_token,
                max_messages=max_messages,
                bot=self.bot
            )

            self.attributes.watched_links = [
                i["Link"] for i in Parser.extract_links(watched_messages)]

            self.attributes.movie_list.mark_watched(
                self.attributes.watched_links)

            if remove_watched:
                self.attributes.movie_list.remove_by_attribute_value(
                    attribute="Watched",
                    value="True"
                )
