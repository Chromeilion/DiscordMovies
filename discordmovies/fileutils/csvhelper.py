import csv
import os
from typing import List


class CsvHelper:
    """
    A class that helps deal with csv files. Providing useful utilities and
    functions.
    """

    def __init__(self, name: str):
        self.name = self.check_name(name)

    @staticmethod
    def check_name(name: str) -> str:
        if name[:-3] != ".csv":
            return name + ".csv"
        return name

    def exists(self) -> bool:
        """
        Checks if a CSV file with the given name exists already.
        """

        if os.path.exists(self.name):
            return True
        return False

    def get_content(self) -> List[List[str]]:
        """
        Get the contents of the CSV file.
        """
        if not self.exists():
            return []
        with open(self.name, "r+", newline="") as f:
            reader = csv.reader(f)
            return list(reader)

    def write_existing(self, values: List[List[str]], categories: List[str]):
        """
        Write to an existing CSV file. Makes sure to append values instead of
        overwriting old ones. Also checks for correct formatting.
        """

        with open(self.name, "r+", newline="") as f:
            writer = csv.writer(f)
            file_contents = self.get_content()

            if not file_contents:
                writer.writerow(categories)
                f.flush()
                file_contents = self.get_content()

            if file_contents[0] != categories:
                if len(file_contents) > 0:
                    raise AttributeError("CSV File is incorrectly"
                                         "formatted. Please create"
                                         "a new one.")

            for i in values:
                writer.writerow(i)

    def write_new(self, values: List[List[str]]):
        """
        Creates a new CSV file and writes to it.
        """
        with open(self.name, "w", newline="") as f:
            writer = csv.writer(f)

            for i in values:
                writer.writerow(i)
