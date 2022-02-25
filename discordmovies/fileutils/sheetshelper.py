from discordmovies.fileutils.docsutils import DocsHandler
from typing import List


class SheetsHelper:
    """
    A class that helps deal with Google Sheets. Providing useful high level
    utilities and functions.
    """

    def __init__(self, spreadsheet_id: str = None):
        self.handler = DocsHandler(spreadsheet_id=spreadsheet_id)
        self.handler.setup_docs()

    def check_existence(self) -> bool:
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
            return False

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

    def write(self, values: List[List[str]]):
        """
        Format and write to an already existing sheet.
        """

        self.format_sheet()
        self.handler.append_sheet(values=values)

    def write_new(self, values: List[List[str]], title: str):
        """
        Create a new sheet, format it, and write to it.
        """
        self.handler.create_sheet(title=title)
        self.format_sheet()
        self.handler.fill_sheet(inputs=values)
