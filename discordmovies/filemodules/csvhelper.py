import csv
import os
from typing import List
from discordmovies.attributes import DiscordMoviesAttributes


class CsvHelper:
    """
    A class that helps deal with csv files. Providing useful utilities and
    functions.
    """

    def __init__(self, attributes: DiscordMoviesAttributes):
        self.attributes = attributes
        self.name = self.check_name(self.attributes.name)

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

    def get_values(self) -> List[List[str]]:
        """
        Get the contents of the CSV file.
        """
        if not self.exists():
            return []
        with open(self.name, "r+", newline="") as f:
            reader = csv.reader(f)
            return list(reader)

    def write_existing(self):
        """
        Write to an existing CSV file. Makes sure to append values instead of
        overwriting old ones. Also checks for correct formatting.
        """

        values = self.attributes.movie_list.get_movies_list(
            format_images=False,
            attributes_key=False)
        categories = self.attributes.movie_list.get_categories()

        with open(self.name, "r+", newline="") as f:
            writer = csv.writer(f)
            file_contents = self.get_values()

            if not file_contents:
                writer.writerow(categories)
                f.flush()
                file_contents = self.get_values()

            if file_contents[0] != categories:
                if len(file_contents) > 0:
                    raise AttributeError("CSV File is incorrectly"
                                         "formatted. Please create"
                                         "a new one.")

            for i in values:
                writer.writerow(i)

    def write_new(self):
        """
        Creates a new CSV file and writes to it.
        """

        values = self.attributes.movie_list.get_movies_list(format_images=False)

        with open(self.name, "w", newline="") as f:
            writer = csv.writer(f)

            for i in values:
                writer.writerow(i)
