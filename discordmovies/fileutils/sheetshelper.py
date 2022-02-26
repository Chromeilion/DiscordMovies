from discordmovies.fileutils.docsutils import DocsHandler
from typing import List
from discordmovies.discordmoviesattributes import DiscordMoviesAttributes


class SheetsHelper:
    """
    A class that provides useful high level
    utilities and functions for Google Sheets.
    """

    def __init__(self, attributes: DiscordMoviesAttributes,
                 spreadsheet_id: str = None):
        self.attributes = attributes
        self.handler = DocsHandler(spreadsheet_id=spreadsheet_id)
        self.handler.setup_docs()

    def exists(self) -> bool:
        return self.handler.check_existence()

    def get_values(self) -> List[List[str]]:
        """
        Get all values from the sheet. Returns an empty list if there are none.
        """
        sheet = self.handler.get_doc_contents()
        try:
            return sheet["values"]
        except KeyError:
            return []

    def remove_row_not_listed(self, values: List[str], column: int,
                              ignore: List[List[str]]) -> bool:
        """
        Remove a row if the value in its column isn't in a list. You can also
        specify which rows to ignore in a list. When specifying what row to
        ignore, you must pass the exact string representation of the entire row.
        """

        if not values:
            if not self.attributes.links:
                return False
            return True

        removal_list = []

        contents = self.handler.get_doc_contents()["values"]

        for k, i in enumerate(contents):
            if i in ignore:
                continue
            elif not any([j in i[column] for j in values]):
                removal_list.append(k)

        removal_list.reverse()

        for i in removal_list:
            self.handler.remove_row(i, i+1)

        return True

    def format_sheet(self, row_height: int = 148,
                     first_row_height: int = 30):
        """
        Format a sheet to make it look pretty.
        """

        self.handler.adjust_row_height(row_height)
        self.handler.adjust_row_height(height=first_row_height, start_row=0,
                                       end_row=1)
        self.handler.set_alignment()

    def write_existing(self):
        """
        Format and write to an already existing sheet.
        """

        values = self.attributes.movie_list.get_movies_list(
            attributes_key=False)
        check_links = self.attributes.links
        check_column = self.attributes.movie_list.get_cat_indexes()["Link"]
        categories = self.attributes.movie_list.get_categories()
        ignore_column = [categories]

        # It's important to store the output of remove_row_not_listed
        # because it returns False if the sheet is empty. If the Sheet's
        # empty, we need to add headers to the top.
        sheet_full = self. \
            remove_row_not_listed(values=check_links,
                                  column=check_column,
                                  ignore=ignore_column)

        if not sheet_full:
            values.insert(0, categories)

        self.format_sheet()
        self.handler.append_sheet(values=values)

    def write_new(self):
        """
        Create a new sheet, format it, and write to it.
        """

        values = self.attributes.movie_list.get_movies_list()

        self.handler.create_sheet(title=self.attributes.name)
        self.format_sheet()
        self.handler.fill_sheet(inputs=values)
