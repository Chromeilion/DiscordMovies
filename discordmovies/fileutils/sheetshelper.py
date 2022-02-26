from discordmovies.fileutils.docsutils import DocsHandler
from typing import List, Union
from discordmovies.attributes import DiscordMoviesAttributes


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

    def get_values(self, column: str = None) -> Union[List[List[str]],
                                                      List[str]]:
        """
        Get all values from the sheet. Returns an empty list if there are none.
        Can specify a column if you only wish to get values from a certain
        column.
        """
        sheet = self.handler.get_doc_contents()
        try:
            values = sheet["values"]
        except KeyError:
            return []

        if column:
            column_index = self.attributes.movie_list.get_cat_indexes()[column]
            return [i[column_index] for i in values]
        else:
            return values

    def remove_row_not_listed(self, values: List[str], column: int,
                              ignore: List[List[str]]) -> bool:
        """
        Remove a row if the value in its column isn't in a list. You can also
        specify which rows to ignore in a list. When specifying what row to
        ignore, you must pass the exact string representation of the entire row.
        """

        removal_list = []

        contents = self.get_values()

        for k, i in enumerate(contents):
            if i in ignore:
                continue
            elif not any([j in i[column] for j in values]):
                removal_list.append(k)

        removal_list.reverse()

        for i in removal_list:
            self.handler.remove_row(i, i + 1)

        return True

    def remove_row_listed(self, values: List[str], column: int):
        """
        Remove a row if the contents of one of its column matches a value/s.
        """

        removal_list = []

        contents = self.get_values()

        for k, i in enumerate(contents):
            if any([j in i[column] for j in values]):
                removal_list.append(k)

        removal_list.reverse()

        for i in removal_list:
            self.handler.remove_row(i, i + 1)

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

    def update_watched(self, values: List[str]):
        """
        Checks values in a column and updates them if they are different from
        a the value entered.
        """

        column_id = self.attributes.movie_list.get_cat_indexes()["Watched"]
        row_indexes = []

        for k, i in enumerate(self.get_values(column="Link")):
            if any(j in i for j in values):
                row_indexes.append(k)

        for i, j in enumerate(self.get_values(column="Watched")):
            if i == 0:
                continue
            if i in row_indexes:
                if j != "TRUE":
                    self.handler.update_value(value=[["TRUE"]],
                                              start_index=(column_id, i),
                                              stop_index=(column_id, i))
            else:
                self.handler.update_value(value=[["FALSE"]],
                                          start_index=(column_id, i),
                                          stop_index=(column_id, i))

    def write_existing(self):
        """
        Format and write to an already existing sheet.
        """

        values = self.attributes.movie_list.get_movies_list(
            attributes_key=False)
        check_column = self.attributes.movie_list.get_cat_indexes()["Link"]
        categories = self.attributes.movie_list.get_categories()
        ignore_column = [categories]

        self.remove_row_not_listed(values=self.attributes.links,
                                   column=check_column,
                                   ignore=ignore_column)

        if not self.get_values():
            values.insert(0, categories)
        else:
            self.update_watched(values=self.attributes.watched_links)

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
