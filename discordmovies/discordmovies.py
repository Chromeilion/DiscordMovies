from tqdm import tqdm
from discordmovies.parser import Parser
from discordmovies.scrapper import Scrapper
from typing import Union
from discordmovies.exceptions import MovieIdentityError


class DiscordMovies:
    """
    A class for going through a discord movie recommendations channel and
    extracting all links. These links can then be uploaded to Google Sheets
    or exported to a CSV.
    """

    def __init__(self, discord_auth_token: Union[str, int], bot: bool = True):
        self.auth_token = discord_auth_token
        self.scrapper = Scrapper()
        self.content = None
        self.bot = bot
        self.categories = self.get_categories()

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

        # Check if links have already been calculated and calculate them if not.
        if self.content is None:
            self.get_links(channel_id=channel_id, max_messages=max_messages,
                           tmdb_api_key=tmdb_api_key)

            content_sheets = [self.categories]
            for i in self.content[1:]:
                image = [f'=IMAGE("{i[0]}")'] + i[1:]
                content_sheets.append(image)

        elif type(self.content) == "list":
            content_sheets = self.content

        else:
            raise ValueError("self.content should be of type 'list' or 'None', it is neither.")

        # Write to Google Sheets. If the sheet exists, then new links get
        # appended. Otherwise, a new sheet is created and values are filled.
        handler = DocsHandler(spreadsheet_id=sheet_id)
        handler.setup_docs()

        if not handler.check_existence():
            handler.create_sheet(title=sheet_name)
            self.format_sheet(handler=handler)
            handler.fill_sheet(content_sheets)

        else:
            sheet = handler.get_doc_contents()

            content_sheets = [self.categories]
            for i in self.content:
                image = [f'=IMAGE("{i[0]}")'] + i[1:]
                content_sheets.append(image)

            try:
                values = sheet["values"]
            except KeyError:
                values = None

            if values is not None:
                dupes = []
                names = [i[1] for i in content_sheets]
                for i in values:
                    if i[1] in names:
                        dupes.append(i[1])

                content_sheets = [i for i in content_sheets if i[1]
                                  not in dupes]

            self.format_sheet(handler=handler)
            handler.append_sheet(content_sheets)

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

        # Check if links have already been calculated.
        if self.content is None:
            self.get_links(channel_id=channel_id, max_messages=max_messages,
                           tmdb_api_key=tmdb_api_key)

        # Check if the csv already exists and whether we need to rewrite it
        # or not.
        if os.path.exists(csv_name):
            print("CSV file exists, assuming correct formatting and appending "
                  "new values.")
            titles = [i[1] for i in self.content]
            dupes = []
            with open(csv_name, "r+", newline="") as f:
                for i in csv.reader(f):
                    if i[1] in titles:
                        dupes.append(i[1])

                self.content = [i for i in self.content if i[1] not in dupes]

                writer = csv.writer(f)
                for i in self.content:
                    writer.writerow(i)
        else:
            print("No CSV file found, creating new one.")
            with open(csv_name, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.categories)

                for i in self.content:
                    writer.writerow(i)

    def get_links(self, channel_id: Union[str, int], max_messages: int = 100,
                  tmdb_api_key: str = None):
        """
        Gets messages and parses them, then it gets rid of duplicates and non-movie links.
        The output goes into self.content.
        """

        # Get all messages from channel
        messages = self.scrapper.get_messages(channel_id=channel_id,
                                              auth=self.auth_token,
                                              max_messages=max_messages,
                                              bot=self.bot)

        # Extract all links from messages
        links = Parser.extract_links(messages)

        self.content = []
        failures = []
        # Create list with all links and metadata
        for i in tqdm(links, unit=" movies", desc="gathering metadata"):
            try:
                metadata = self.scrapper.get_metadata(i[0], tmdb_api_key)
            except MovieIdentityError:
                failures.append(i)
                continue

            [metadata.append(j) for j in i[1::]]
            self.content.append(metadata)

        print("The following movies were not found:")
        print('\n'.join(map(str, failures)))

        self.handle_duplicates()

    @staticmethod
    def format_sheet(handler, row_height: int = 148,
                     first_row_height: int = 30):
        """
        Format a sheet correctly.
        """

        handler.adjust_row_height(row_height)
        handler.adjust_row_height(height=first_row_height, start_row=0,
                                  end_row=1)
        handler.set_alignment()

    def handle_duplicates(self, ignore: list = None):
        """
        Checks for duplicate entries, and if it finds them, combines them into one entry where applicable.
        Optionally a variable "ignore" can be passed. This should be a list of columns that should be ignored when
        combining duplicates. What this means is that when combining duplicates, only the first value in the ignored
        column will stay and all duplicate values will be deleted.
        """

        if ignore is None:
            ignore = ["Poster", "Title", "Runtime", "Trailer", "User Score"]

        titles = [i[self.scrapper.get_columns()["Title"]] for i in self.content]

        # Get list of duplicates
        duplicates = Parser().check_duplicates(titles)

        ignore_indexes = []
        categories = self.scrapper.get_columns()
        for i in ignore:
            ignore_indexes.append(categories[i])

        removal_list = []

        # Iterate through the duplicates and merge them into one entry.
        # Duplicates don't get deleted here, because it would mess up the
        # indexing.
        for i in duplicates:
            if len(duplicates[i]) > 1:
                minimum_dupe = min(duplicates[i])
                dupes_minus_min = [n for n in duplicates[i] if n != min(duplicates[i])]
                removal_list += dupes_minus_min

                for j in dupes_minus_min:
                    for k, m in enumerate(self.content[minimum_dupe]):
                        if k in ignore_indexes:
                            continue
                        elif self.content[j][k] not in m:
                            self.content[minimum_dupe][k] += f"\n{self.content[j][k]}"

        # Now we remove duplicates if there are any.
        if len(removal_list) > 0:
            removal_list.sort(reverse=True)

            for i in removal_list:
                del self.content[i]

    def get_categories(self):
        columns = [i[0] for i in self.scrapper.get_sorted_columns()]
        columns.extend(["Link", "User"])
        return columns
