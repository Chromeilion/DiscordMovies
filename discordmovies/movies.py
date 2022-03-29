from tqdm import tqdm
from discordmovies.exceptions import MovieIdentityError
from discordmovies.utils import Utils
from typing import Union, List, Dict
import copy


class MovieCategories:
    """
    A class that contains the possible attributes a movie could have.
    """

    def __init__(self, categories: List[str] = None,
                 exclude_categories: List[str] = None):

        self.all_categories = ["Poster", "Title", "Genres", "Runtime",
                               "Trailer", "User Score", "ID", "Link",
                               "Date Suggested", "User", "Watched"]

        necessary_categories = ["Title", "Link"]

        if categories is None:
            self.categories = self.all_categories.copy()

        else:
            if all([i in categories for i in necessary_categories]) and all(
                    [i in self.all_categories for i in categories]):
                self.categories = categories

            else:
                raise AttributeError("Title and Link categories must be "
                                     "present and categories must be "
                                     "supported.")

        if exclude_categories is not None:
            if all([i not in necessary_categories for i in exclude_categories]
                   ) and all([i in self.all_categories for i in
                              exclude_categories]):
                [self.categories.remove(i) for i in exclude_categories]

            else:
                raise AttributeError("Excluded categories must not be necessary"
                                     "categories, and they must be real"
                                     "categories.")

    def get_categories(self) -> List[str]:
        return self.categories.copy()

    def get_cat_indexes(self) -> Dict[str, int]:
        cat_dict = {}
        for i, j in enumerate(self.categories):
            cat_dict[j] = i

        return cat_dict

    def get_all_categories(self):
        """
        Get a list of all available categories.
        """

        return self.all_categories

    def check_attribute(self, attribute: str) -> bool:
        """
        Checks if an attribute is valid. Returns False if it is not, and True
        otherwise.
        """
        if attribute not in self.categories:
            return False
        return True

    def copy(self):
        return copy.deepcopy(self)


class Movie(MovieCategories):
    """
    A data structure that represents a movie. Includes movie information and
    the ability to get the information in various forms. Also includes tools
    for getting movie metadata.
    """

    def __init__(self, categories: List[str] = None, values: dict = None,
                 exclude_categories: List[str] = None):
        super().__init__(categories=categories,
                         exclude_categories=exclude_categories)
        self.info = {}
        for i in self.categories:
            self.info[i] = "None"

        if values is not None:
            for i in values:
                self.info[i] = values[i]

    def __getitem__(self, key: str) -> str:
        return self.info[key]

    def __setitem__(self, key: str, value: str) -> bool:
        if not isinstance(key, str):
            raise TypeError("The key must be a string in a Movie object.")
        if not isinstance(value, str):
            raise TypeError("The value must be a string in a Movie object.")

        if key not in self.categories:
            return False
        self.info[key] = value

    def items(self):
        return self.info.items()

    def get_list(self, attribute: List[str] = None) -> list:
        """
        Values from a Movie object in the form of a list. Can specify
        specifically what attributes you'd like in the form of a list of
        attribute names.
        """

        if attribute is None:
            attribute = self.get_categories()

        return [self[i] for i in attribute]

    def fill_metadata(self, omdb_api_key: str):
        """
        Get metadata for movie and store it.
        """
        from discordmovies.inputmodules.metadata.metadata import Metadata

        Metadata().get_metadata(movie=self, omdb_api_key=omdb_api_key)

    def format_image(self, attribute: Union[str, List[str]] = "Poster"):
        """
        Format an attribute so that it displays nicely in Google Sheets as an
        image. Can accept multiple attributes in the form of a list. The
        attribute should be a link to an image. By default, edits
        the "Poster" attribute.
        """

        if isinstance(attribute, list):
            for i in attribute:
                self[i] = f'=IMAGE("{self[i]}")'
        elif isinstance(attribute, str):
            self[attribute] = f'=IMAGE("{self[attribute]}")'
        else:
            raise TypeError("Variable 'attribute' must be of type 'list' or "
                            "'str'.")


class MovieList(MovieCategories):
    """
    A place to store Movie objects. Can be used to manipulate multiple movies
    at once in various ways.
    """

    def __init__(self, categories: List[str] = None, items: List[Movie] = None,
                 exclude_categories: List[str] = None):
        super().__init__(categories=categories,
                         exclude_categories=exclude_categories)
        if items is None:
            self.movies = list()
        else:
            self.movies = list(items)

    def __getitem__(self, item: int) -> Movie:
        return self.movies[item]

    def __bool__(self) -> bool:
        return bool(self.movies)

    def __delitem__(self, key: int):
        del self.movies[key]

    def __len__(self):
        return len(self.movies)

    @staticmethod
    def check_movie(item) -> bool:
        """
        Check if an item is of the Movie class.
        """
        if not isinstance(item, Movie):
            return False
        return True

    def append(self, item: Movie):
        """
        Append a movie to the list.
        """

        if not self.check_movie(item):
            raise TypeError("Item must be a Movie object.")

        self.movies.append(item)

    def append_with_metadata(self, item: Movie, omdb_api_key: str):
        """
        Append a movie to the list, and also fill the movies metadata.
        """

        if not self.check_movie(item):
            raise TypeError("Item must be a Movie object.")

        try:
            item.fill_metadata(omdb_api_key)
            self.movies.append(item)

        except MovieIdentityError:
            print(f"cannot insert {item['Link']}, getting metadata failed, "
                  f"skipping")

    def remove(self, movie: Movie):
        self.movies.remove(movie)

    def search(self, value: str, attribute: str) -> list:
        """
        Search for a movie based on the value of an attribute. For example,
        with attribute = "Title" and value = "Joker", will return a list with
        the movie Joker if it is in the list.

        Partial matches are also returned.

        This method hasn't really been tested, so it may be buggy.
        """

        if not self.movies:
            return []

        if attribute not in self.movies[0].get_categories():
            raise AttributeError("Attribute not found!")

        matches = []
        for i in self.movies:
            if value in i[attribute]:
                matches.append(i)

        return matches

    def get_movies_list(self, attributes_key: bool = True,
                        attributes: Union[str, List[str]] = None,
                        format_images: bool = True,
                        format_images_attribute: str =
                        "Poster") -> List[List[str]]:
        """
        Get a list of all movies, can add an attributes key to the first
        position of the list. By default, has all attributes, however you can
        choose which ones you'd like with a list.

        By default, formats images for Google Sheets. When formatting,
        transformations are not in-place, the output is a copy.
        """

        if not self.movies:
            return []

        if attributes is None:
            attributes = self.get_categories()

        if format_images:
            movies_list = self.copy()
            movies_list.format_images(attribute=format_images_attribute)
        else:
            movies_list = self

        movies_list = [i.get_list(attribute=attributes) for i in
                       movies_list.movies]

        if attributes_key:
            attribute_key_values = self.get_categories()
            for i in attributes:
                if i not in attribute_key_values:
                    attribute_key_values.remove(i)

            movies_list.insert(0, attribute_key_values)

        return movies_list

    def fill_all_metadata(self, tmdb_api_key: str):
        """
        Fill metadata for all movies in list.
        """
        failures = []
        if self:
            for i in tqdm(self, unit=" movies",
                          desc="gathering metadata"):
                try:
                    i.fill_metadata(omdb_api_key=tmdb_api_key)
                except MovieIdentityError:
                    failures.append(i)

            if len(failures) > 0:
                print("The following movies were not found:")
                print('\n'.join(map(str, [i["Link"] for i in failures])))

                for i in failures:
                    self.remove(i)

    def merge_duplicates(self, ignore: List[str] = None,
                         attribute: str = "Title"):
        """
        Checks for duplicate entries. If any are found, they are combined.

        The ignore list is a list of attributes which should not be combined.
        In this case, the first attribute found will be taken, and attributes
        which are not ignored will be combined.

        For example, with the two attributes 'Title' and 'Link', when ignoring
        the 'Title' attribute, two films would be combined such that the 'Title'
        attribute of the first is used, meaning in the combined cell there's
        only a single value for 'Title', even if the values were different.
        Meanwhile, the attribute 'Link' would have two values, one from each
        movie.

        You can specify what attribute to use when searching for duplicates
        with the variable "attribute". By default, the title is used.
        """

        if ignore is None:
            ignore = self.get_categories()
            # Links should be saved most of the time to preserve the integrity
            # of other functions.
            ignore.remove('Link')

        attributes = [i.get_list([attribute]) for i in self]

        duplicates = Utils().check_duplicates(attributes)

        categories = self.get_categories()

        for i in ignore:
            if i not in categories:
                raise ValueError("Ignored attributes must be actual "
                                 "attributes.")

        removal_list = []

        # Iterate through the duplicates and merge them into one entry.
        # Duplicates don't get deleted here, because it would mess up the
        # indexing.
        for i in duplicates:
            if len(duplicates[i]) > 1:
                minimum_dupe = min(duplicates[i])
                dupes_minus_min = [n for n in duplicates[i] if n != min(
                    duplicates[i])]
                removal_list += dupes_minus_min

                for j in dupes_minus_min:
                    for m in self[minimum_dupe].items():
                        if m[0] in ignore:
                            pass
                        elif self[j][m[0]] not in m[1]:
                            self[minimum_dupe][m[0]] += f"\n{self[j][m[0]]}"

        # Now we remove duplicates if there are any.
        if len(removal_list) > 0:
            removal_list.sort(reverse=True)

            for i in removal_list:
                del self[i]

    def format_images(self, attribute: Union[str, List[str]] = "Poster"):
        """
        Formats one or multiple attributes into a format good for Google Sheets
        images.
        """

        for i in self:
            i.format_image(attribute=attribute)

    def remove_by_attribute_value(self, attribute: str,
                                  value: Union[str, List[str]]):
        """
        Remove all movies with attribute equal to a specific value/s. Will
        remove movies where a substring matches the value as well.
        """

        if not self.check_attribute(attribute=attribute):
            raise ValueError("The given attribute is not valid.")

        if isinstance(value, list):
            removal_list = []

            for i in self:
                for j in value:
                    if i[attribute] in j:
                        removal_list.append(i)
                        break

            [self.movies.remove(i) for i in removal_list]

        elif isinstance(value, str):
            for i in self:
                if value in i[attribute]:
                    self.remove(i)

    def mark_watched(self, watched_links: List[str]):
        """
        Marks movies as watched if they can be found on a list of links, and
        not watched if they cannot be found.
        """

        for i in self:
            if any(j in i["Link"] for j in watched_links):
                i["Watched"] = "True"
            else:
                i["Watched"] = "False"
