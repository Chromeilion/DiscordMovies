from discordmovies.parser import Parser
from typing import Union
from discordmovies.movies import Movie
from discordmovies.discordmoviesattributes import DiscordMoviesAttributes
from discordmovies.scrapper import Scrapper


class DiscordMovies:
    """
    A class for going through a discord movie recommendations channel and
    extracting all links. These links can then be uploaded to Google Sheets
    or exported to a CSV.
    """

    def __init__(self, discord_auth_token: Union[str, int], bot: bool = True,
                 doc_name: str = "discordmovies"):
        self.scrapper = Scrapper()
        self.auth_token = discord_auth_token
        self.bot = bot
        self.attributes = DiscordMoviesAttributes(name=doc_name)

    def discord_to_sheets(self, channel_id: Union[str, int],
                          sheet_id: Union[str, int] = None,
                          max_messages: int = 100,
                          tmdb_api_key: str = None):
        """
        Takes all links from a discord channel and creates a Google Sheets
        document from them. If the document exists, it will only add links
        which do not exist already.
        """
        from discordmovies.fileutils.sheetshelper import SheetsHelper

        sheets_helper = SheetsHelper(attributes=self.attributes,
                                     spreadsheet_id=sheet_id)

        if sheets_helper.check_existence():
            if sheets_helper.check_existence():
                if not self.attributes.movie_list:
                    self.get_links(channel_id=channel_id,
                                   max_messages=max_messages,
                                   tmdb_api_key=tmdb_api_key,
                                   current_content=sheets_helper.get_values())
                sheets_helper.write_existing()
            else:
                if not self.attributes.movie_list:
                    self.get_links(channel_id=channel_id,
                                   max_messages=max_messages,
                                   tmdb_api_key=tmdb_api_key)
                sheets_helper.write_new()

    def discord_to_csv(self, channel_id: Union[str, int],
                       max_messages: int = 100,
                       tmdb_api_key: str = None):
        """
        Takes all links from a discord channel, parses them,
        and dumps them into a CSV file.
        """
        from discordmovies.fileutils.csvhelper import CsvHelper
        csv_helper = CsvHelper(self.attributes)

        if csv_helper.exists():
            if not self.attributes.movie_list:
                self.get_links(channel_id=channel_id,
                               max_messages=max_messages,
                               tmdb_api_key=tmdb_api_key,
                               current_content=csv_helper.get_content())

            print("CSV file exists, appending new values.")
            csv_helper.write_existing()
        else:
            if not self.attributes.movie_list:
                self.get_links(channel_id=channel_id,
                               max_messages=max_messages,
                               tmdb_api_key=tmdb_api_key)
            print("No CSV file found, creating new one.")
            csv_helper.write_new()

    def get_links(self, channel_id: Union[str, int], max_messages: int = 100,
                  tmdb_api_key: str = None,
                  current_content: list = None):
        """
        Gets messages and parses them, then it gets rid of duplicates and
        non-movie links, as well as movies already present in current_content.
        The output goes into self.content.
        """

        # Get all messages from channel
        messages = self.scrapper.get_messages(channel_id=channel_id,
                                              auth=self.auth_token,
                                              max_messages=max_messages,
                                              bot=self.bot)

        # Extract all links from messages
        self.attributes.links = Parser.extract_links(messages)
        for i in self.attributes.links:
            self.attributes.movie_list.append(Movie(values=i))

        self.attributes.links = [i['Link'] for i in self.attributes.links]

        if current_content is not None:
            link_index = self.attributes.movie_list.get_cat_indexes()["Link"]
            self.attributes.links = [i[link_index] for i in current_content
                                     if i != []]
            self.attributes.movie_list.remove_by_attribute_value(
                attribute="Link",
                value=self.attributes.links)

        self.attributes.movie_list.fill_all_metadata(tmdb_api_key)
        self.attributes.movie_list.merge_duplicates()
