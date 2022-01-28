import re
from urllib.parse import urlparse


class Parser:
    """
    A class that contains functions for parsing Discord messages.
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
                        links.append(k)
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

        if url_parsed.hostname in ["anilist.co", "myanimelist.net"]:
            for i, j in enumerate(path_split):
                if j == "anime":
                    content_id = path_split[i+1]

        elif url_parsed.hostname in ["www.imdb.com", "m.imdb.com"]:
            for i, j in enumerate(path_split):
                if j == "title":
                    content_id = path_split[i+1]
                    break

        else:
            content_id = None

        return url_parsed.hostname, content_id
