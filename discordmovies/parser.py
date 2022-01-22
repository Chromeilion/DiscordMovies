import re


class Parser:
    """
    A class that contains functions for parsing Discord messages contained
    within a dictionary.
    """
    def __init__(self, messages: list = None):
        self.messages = messages

    def set_messages(self, messages: list):
        self.messages = messages

    def extract_links(self) -> list:
        """
        Go through jsons returned by Scrapper and extract links from message
        contents.
        """
        links = []
        for i in self.messages:
            for j in i:
                re_obj = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+',
                                    str(j["content"]))
                if re_obj:
                    for k in re_obj:
                        links.append([k])
        return links
