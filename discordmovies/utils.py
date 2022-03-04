class Utils:
    """
    A class containing utility functions that can be used by other classes in
    discordmovies.
    """

    @staticmethod
    def check_duplicates(links: list) -> dict:
        """
        Takes a list and finds all duplicates. Returns a dictionary with the
        indexes for each item. If there are multiple occurrences of that item
        there will be multiple indexes.
        The list should ideally contain strings.
        """
        from collections import defaultdict

        dupes = defaultdict(list)

        for i, item in enumerate(links):
            dupes[item[0]].append(i)

        return dupes
