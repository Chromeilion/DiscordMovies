from discordmovies.parser import Parser
from discordmovies.scrapper import Scrapper
from typing import Union
from discordmovies.movies import Movie, MovieList


class DiscordMovies:
    """
    A class for going through a discord movie recommendations channel and
    extracting all links. These links can then be uploaded to Google Sheets
    or exported to a CSV.
    """

    def __init__(self, discord_auth_token: Union[str, int], bot: bool = True):
        self.auth_token = discord_auth_token
        self.scrapper = Scrapper()
        self.movie_list = MovieList()
        self.bot = bot
        self.links = []

    def discord_to_sheets(self, channel_id: Union[str, int],
                          sheet_id: Union[str, int] = None,
                          sheet_name: str = "DiscordMovies",
                          max_messages: int = 100,
                          tmdb_api_key: str = None):
        """
        Takes all links from a discord channel and creates a Google Sheets
        document from them. If the document exists, it will only add links
        which do not exist already.
        """
        from discordmovies.fileutils.sheetshelper import SheetsHelper

        sheets_helper = SheetsHelper(spreadsheet_id=sheet_id)

        # If the Google Sheet already exists the operations that need to be
        # done are different.
        if sheets_helper.check_existence():
            values = sheets_helper.get_values()

            # Dont calculate the movie_list again if its already been
            # calculated.
            if not self.movie_list:
                self.get_links(channel_id=channel_id, max_messages=max_messages,
                               tmdb_api_key=tmdb_api_key,
                               current_content=values)

            self.movie_list.format_images()

            # It's important to store the output of remove_row_not_listed
            # because it returns False if the sheet is empty. If the Sheet's
            # empty, we need to add headers to the top.
            sheet_not_empty = sheets_helper. \
                remove_row_not_listed(values=self.links,
                                      column=self.movie_list.get_cat_indexes(
                                      )["Link"],
                                      ignore=[self.movie_list.get_categories()])

            if sheet_not_empty:
                content_sheets = self.movie_list.get_movies_list(
                    attributes_key=False)
            else:
                content_sheets = self.movie_list.get_movies_list()

            sheets_helper.write(content_sheets)

        else:
            self.get_links(channel_id=channel_id, max_messages=max_messages,
                           tmdb_api_key=tmdb_api_key)
            self.movie_list.format_images()
            content_sheets = self.movie_list.get_movies_list()
            sheets_helper.write_new(values=content_sheets,
                                    title=sheet_name)

    def discord_to_csv(self, channel_id: Union[str, int],
                       csv_name: str = "DiscordMovies",
                       max_messages: int = 100,
                       tmdb_api_key: str = None):
        """
        Takes all links from a discord channel, parses them,
        and dumps them into a CSV file.
        """
        from discordmovies.fileutils.csvhelper import CsvHelper
        csv_helper = CsvHelper(name=csv_name)

        if csv_helper.exists():
            if not self.movie_list:
                self.get_links(channel_id=channel_id,
                               max_messages=max_messages,
                               tmdb_api_key=tmdb_api_key,
                               current_content=csv_helper.get_content())

            print("CSV file exists, appending new values.")
            csv_helper.write_existing(values=self.movie_list.get_movies_list(),
                                      categories=self.movie_list.
                                      get_categories())
        else:
            if not self.movie_list:
                self.get_links(channel_id=channel_id,
                               max_messages=max_messages,
                               tmdb_api_key=tmdb_api_key)
            print("No CSV file found, creating new one.")
            csv_helper.write_new(values=self.movie_list.get_movies_list())

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
        self.links = Parser.extract_links(messages)
        for i in self.links:
            self.movie_list.append(Movie(values=i))

        self.links = [i['Link'] for i in self.links]

        if current_content is not None:
            link_index = self.movie_list.get_cat_indexes()["Link"]
            links = [i[link_index] for i in current_content if i != []]
            self.movie_list.remove_by_attribute_value(attribute="Link",
                                                      value=links)

        self.movie_list.fill_all_metadata(tmdb_api_key)
        self.movie_list.merge_duplicates()
