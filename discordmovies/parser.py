import re
from urllib.parse import urlparse


class Parser:
    """
    A class that contains functions for parsing Discord messages and movie links.
    """

    @staticmethod
    def extract_links(messages) -> list:
        """
        Go through jsons returned by Scrapper and extract links from message
        contents.
        """
        links = []
        for i in messages:
            for j in i:
                re_obj = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+',
                                    str(j["content"]))
                if re_obj:
                    for k in re_obj:
                        links.append((k, j['author']['username']))
        return links

    @staticmethod
    def identify(link: str) -> tuple:
        """
        Takes a supported link and splits it into pieces. It analyzes it and
        returns the hostname and ID. If the website is not supported returns
        ID as None.
        """

        url_parsed = urlparse(link)
        path_split = url_parsed.path.split("/")
        content_id = None

        if url_parsed.hostname in ["anilist.co", "myanimelist.net"]:
            for i, j in enumerate(path_split):
                if j == "anime":
                    content_id = path_split[i+1]
                    break

        elif url_parsed.hostname in ["www.imdb.com", "m.imdb.com"]:
            for i, j in enumerate(path_split):
                if j == "title":
                    content_id = path_split[i+1]
                    break

        return url_parsed.hostname, content_id

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
            dupes[item].append(i)

        return dupes
