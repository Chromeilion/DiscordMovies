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
        from discordmovies.docshandler import DocsHandler

        handler = DocsHandler(spreadsheet_id=sheet_id)
        handler.setup_docs()

        if handler.check_existence():
            sheet = handler.get_doc_contents()

            try:
                values = sheet["values"]
            except KeyError:
                values = None

            if not self.movie_list:
                self.get_links(channel_id=channel_id, max_messages=max_messages,
                               tmdb_api_key=tmdb_api_key,
                               current_content=values)

            self.movie_list.format_images()

            if not values:
                content_sheets = self.movie_list.get_movies_list()
            else:
                print("Removing movies which are no longer in Discord.")
                handler.remove_row_not_list(
                    values=self.links,
                    column=self.movie_list.
                    get_cat_indexes()["Link"],
                    ignore=[self.movie_list.get_categories()])

                content_sheets = self.movie_list.get_movies_list(
                    attributes_key=False)

            self.movie_list.format_images()
            handler.format_sheet()
            handler.append_sheet(content_sheets)

        else:
            self.get_links(channel_id=channel_id, max_messages=max_messages,
                           tmdb_api_key=tmdb_api_key)
            self.movie_list.format_images()
            content_sheets = self.movie_list.get_movies_list()
            handler.create_sheet(title=sheet_name)
            handler.format_sheet()
            handler.fill_sheet(content_sheets)

    def discord_to_csv(self, channel_id: Union[str, int],
                       csv_name: str = "DiscordMovies",
                       max_messages: int = 100,
                       tmdb_api_key: str = None):
        """
        Takes all links from a discord channel, parses them,
        and dumps them into a CSV file.
        """
        import csv
        import os

        # Check name provided
        if csv_name[:-3] != ".csv":
            csv_name = csv_name + ".csv"

        # Check if the csv already exists and whether we need to rewrite it
        # or not.
        if os.path.exists(csv_name):
            print("CSV file exists, assuming correct formatting and appending "
                  "new values.")

            with open(csv_name, "r+", newline="") as f:
                reader = csv.reader(f)
                writer = csv.writer(f)

                file_contents = list(reader)
                if not file_contents:
                    writer.writerow(self.movie_list.get_categories())
                    f.flush()
                    file_contents = list(reader)

                if file_contents[0] != self.movie_list.get_categories():
                    if len(file_contents) > 0:
                        raise AttributeError("CSV File is incorrectly"
                                             "formatted. Please create"
                                             "a new one.")

                if not self.movie_list:
                    self.get_links(channel_id=channel_id,
                                   max_messages=max_messages,
                                   tmdb_api_key=tmdb_api_key,
                                   current_content=file_contents)

                for i in self.movie_list.get_movies_list(
                        attributes_key=False):
                    writer.writerow(i)

        else:
            if not self.movie_list:
                self.get_links(channel_id=channel_id,
                               max_messages=max_messages,
                               tmdb_api_key=tmdb_api_key)

            print("No CSV file found, creating new one.")
            with open(csv_name, "w", newline="") as f:
                writer = csv.writer(f)

                for i in self.movie_list.get_movies_list():
                    writer.writerow(i)

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
