from discordmovies.attributes import DiscordMoviesAttributes
from typing import List


class FileHelper:
    """
    Used to abstract the various helpers and unify them under one object.
    """

    def __init__(self, filetype: str, attributes: DiscordMoviesAttributes,
                 sheet_id: str = None, reformat_sheet: bool = None):
        self.filetype = filetype
        if self.filetype == "sheet":
            from discordmovies.filemodules.sheetshelper import SheetsHelper

            self.helper = SheetsHelper(attributes=attributes,
                                       spreadsheet_id=sheet_id,
                                       reformat=reformat_sheet)

        elif self.filetype == "csv":
            from discordmovies.filemodules.csvhelper import CsvHelper
            self.helper = CsvHelper(attributes)
        else:
            raise ValueError(
                "filetype does not match any supported output.")

    def filetype(self) -> str:
        """
        Get the current filetype
        """

        return self.filetype

    def exists(self):
        """
        Check if the file exists already.
        """

        return self.helper.exists()

    def get_values(self) -> List[List[str]]:
        """
        Get all values from the file.
        """

        return self.helper.get_values()

    def write_existing(self, overwrite: bool = False):
        """
        Write to an existing file. If overwrite is set to true the file will be
        overwritten. An important note is that in some cases the file is
        overwritten anyway.
        """

        self.helper.write_existing(overwrite=overwrite)

    def write_new(self):
        """
        Create a new file and write to it.
        """

        self.helper.write_new()
