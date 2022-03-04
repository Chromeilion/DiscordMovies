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

    def write_existing(self, overwrite: bool = False):
        """
        Write to an existing CSV file. The file will be overwritten.
        """
        # Overwrite is a variable, but it does nothing at the moment. It's here
        # mainly as a placeholder. Perhaps it could be used in the future.

        values = self.attributes.movie_list.get_movies_list(
            format_images=False)

        file_contents = self.get_values()
        file_contents.extend(values)
        watched_index = self.attributes.movie_list.get_cat_indexes()[
            "Watched"]
        link_index = self.attributes.movie_list.get_cat_indexes()[
            "Link"]

        removal_list = []

        for k, i in enumerate(file_contents):
            if k == 0:
                continue
            if any([j in i[link_index] for j in
                    self.attributes.watched_links]):
                # My IDE is complaining to me about watched_index here. IDK
                # what's wrong, perhaps something with type hints somewhere?
                i[watched_index] = True
            else:
                i[watched_index] = False

            if not any([j in i[link_index] for j in self.attributes.links]):
                removal_list.append(k)

        if removal_list:
            removal_list.reverse()
            for i in removal_list:
                del self.attributes.movie_list[i]

        self.write_new(values=file_contents)

    def write_new(self, values: List[List[str]] = None):
        """
        Creates a new CSV file and writes to it. Can also overwrite old files.
        """

        if values is None:
            values = self.attributes.movie_list.get_movies_list(
                format_images=False)

        with open(self.name, "w", newline="") as f:
            writer = csv.writer(f)

            for i in values:
                writer.writerow(i)
