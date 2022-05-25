from discordmovies.outputmodules.googleutils import DocsHandler
from typing import List, Union
from discordmovies.attributes import DiscordMoviesAttributes


class SheetsHelper:
    """
    A class that provides useful high level
    utilities and functions for Google Sheets.
    """

    def __init__(self, attributes: DiscordMoviesAttributes,
                 spreadsheet_id: str = None, reformat: bool = False):
        self.attributes = attributes
        self.handler = DocsHandler(spreadsheet_id=spreadsheet_id)
        self.handler.setup_docs()
        self.values = None
        self.reformat = reformat

    def exists(self) -> bool:
        return self.handler.check_existence()

    def get_values(self, column: str = None,
                   force_recalc: bool = False) -> Union[List[List[str]],
                                                        List[str]]:
        """
        Get all values from the sheet. Returns an empty list if there are none.
        Can specify a column if you only wish to get values from a certain
        column.
        """

        if self.values is None or force_recalc:
            if self.exists():
                sheet = self.handler.get_doc_contents()
            else:
                return []
            try:
                self.values = sheet["values"]
            except KeyError:
                self.values = []
                return []

            if column:
                column_index = self.attributes["movie_list"].get_cat_indexes(
                )[column]

                return [i[column_index] for i in self.values]
            else:
                return self.values

        else:
            return self.values

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
        Remove a row if the contents of one of its columns matches a value/s.
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
        self.handler.freeze_row(1)

    def update_watched(self, values: List[str]):
        """
        Checks values in watched column and updates them if they've changed.
        """
        if "Watched" in self.attributes["movie_list"].get_categories():
            column_id = self.attributes["movie_list"].get_cat_indexes()[
                "Watched"]
            row_indexes = []

            for k, i in enumerate(self.get_values(column="Link")):
                if any(j in i for j in values):
                    row_indexes.append(k)

            for i, j in enumerate(self.get_values(column="Watched",
                                                  force_recalc=True)):
                if j == self.attributes["movie_list"].get_categories(
                )[column_id]:
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

        else:
            print("Watched column not found, watched movies not updated.")

    def reformat_sheet(self):
        """
        Re-formats the sheet by deleting all values and reinserting them.
        """

        values = self.get_values(force_recalc=True)
        self.handler.clear_sheet()
        self.format_sheet()
        self.handler.append_sheet(values=values, quiet=True)

    def write_existing(self, overwrite: bool = False):
        """
        Write to an already existing sheet. All new values are appended to the
        end of the sheet. Additionally, the watched attribute is updated for
        all films.

        The overwrite option specifies whether the existing sheet's data should
        be overwritten. It may be overwritten anyway if reformat is set to true.
        Important to note is that only values being currently written to the
        sheet will be on the sheet after a overwrite.
        """

        if overwrite:
            self.handler.clear_sheet()
            values = self.attributes["movie_list"].get_movies_list()
        else:
            values = self.attributes["movie_list"].get_movies_list(
                attributes_key=False)

        link_column = self.attributes["movie_list"].get_cat_indexes()["Link"]
        categories = self.attributes["movie_list"].get_categories()
        ignore_column = [categories]

        if not overwrite:
            self.remove_row_not_listed(values=self.attributes["links"],
                                       column=link_column,
                                       ignore=ignore_column)

        if not self.get_values():
            values.insert(0, categories)

        self.handler.append_sheet(values=values)

        if self.attributes["watched_links"]:
            self.update_watched(values=self.attributes["watched_links"])

        if self.reformat or overwrite:
            self.reformat_sheet()

    def write_new(self):
        """
        Create a new sheet, format it, and write to it.
        """

        values = self.attributes["movie_list"].get_movies_list()

        self.handler.create_sheet(title=self.attributes["name"])
        self.format_sheet()
        self.handler.fill_sheet(inputs=values)
