from discordmovies.parser import Parser
from discordmovies.scrapper import Scrapper
from typing import Union


class DiscordMovies:
    """
    A package for going through a discord movie recommendations channel and
    extracting all links. These links can then be uploaded to Google Sheets
    or exported to a CSV.
    """

    def __init__(self, discord_auth_token: Union[str, int], bot: bool = True,
                 row_height: int = 148):
        self.auth_token = discord_auth_token
        self.scrapper = Scrapper()
        self.content = []
        self.bot = bot
        self.row_height = row_height

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

        # Check if links have already been calculated.
        if len(self.content) == 0:
            self.get_links(channel_id=channel_id, max_messages=max_messages,
                           tmdb_api_key=tmdb_api_key)
            content_sheets = []
            for i in self.content:
                image = [f'=IMAGE("{i[0]}")'] + i[1:]
                content_sheets.append(image)
        else:
            content_sheets = self.content

        # Write to Google Sheets. If the sheet exists, then new links get
        # appended. Otherwise, a new sheet is created and values are filled.
        handler = DocsHandler(spreadsheet_id=sheet_id)
        handler.setup_docs()

        if not handler.check_existence():
            handler.create_sheet(title=sheet_name)
            handler.fill_sheet(content_sheets)
            handler.adjust_row_height(self.row_height)

        else:
            sheet = handler.get_doc_contents()

            for i in sheet["values"]:
                if i in self.content:
                    self.content.remove(i)

            handler.append_sheet(self.content)
            handler.adjust_row_height(self.row_height)

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
        import ast

        # Check name provided
        if csv_name[:-3] != ".csv":
            csv_name = csv_name + ".csv"

        # Check if links have already been calculated.
        if len(self.content) == 0:
            self.get_links(channel_id=channel_id, max_messages=max_messages,
                           tmdb_api_key=tmdb_api_key)

        # Check if the csv already exists and whether we need to rewrite it
        # or not.
        if os.path.exists(csv_name):
            print("CSV file exists, assuming correct formatting and appending "
                  "new values.")
            with open(csv_name, "r+") as f:
                for i in csv.reader(f):
                    if len(i) > 0 and i != ['url']:
                        if ast.literal_eval(i[0]) in self.content:
                            self.content.remove(ast.literal_eval(i[0]))

                writer = csv.writer(f)
                for i in self.content:
                    writer.writerow([i])
        else:
            print("No CSV file found, creating new one.")
            with open(csv_name, "w") as f:
                writer = csv.writer(f)
                writer.writerow(["url"])

                for i in self.content:
                    writer.writerow([i])

    def get_links(self, channel_id: Union[str, int], max_messages: int = 100,
                  tmdb_api_key: str = None):
        """
        Gets messages and parses them, returning links and metadata.
        """

        # Check whether links have already been calculated and skip a few
        # steps if they have.

        # Get all messages from channel
        messages = self.scrapper.get_messages(channel_id=channel_id,
                                              auth=self.auth_token,
                                              max_messages=max_messages,
                                              bot=self.bot)

        # Extract all links from messages
        links = Parser.extract_links(messages)

        # Create list with all links and metadata
        self.content = []
        for i in links:
            metadata = self.scrapper.get_metadata(i, tmdb_api_key)
            self.content.append(metadata)
