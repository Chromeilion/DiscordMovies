import requests
import json
from typing import Union, List, Dict
import re


class Discord:
    """
    Deals with Discord. Getting messages primarily.
    """

    def __init__(self, auth: str, bot: bool, max_messages: int = 100):
        self.bot = bot

        if bot:
            self.headers = {
                "authorization": f"Bot {auth}",
            }
        else:
            self.headers = {
                "authorization": auth,
            }
        self.check_token()
        self.max_messages = max_messages

    def check_token(self) -> bool:
        """
        Check if a discord token is valid.
        """

        r = requests.get(f"https://discordapp.com/api/v9/users/@me",
                         headers=self.headers)
        if r.status_code == 401:
            raise ValueError("The discord token appears to be invalid. If you "
                             "are using a user token make sure --no-bot "
                             "is set.")
        return True

    def get_messages(self, channel_id: Union[int, str]) -> List[str]:
        """
        Get all messages from a Discord channel as a list of dictionaries.
        """

        messages = []
        no_messages = 0
        before = None
        # Discord only lets us collect 100 messages at a time, so to get all
        # of them we need to send a couple requests.
        while no_messages < self.max_messages:
            if before:
                r = requests.get(f"https://discord.com/api/v9/channels/"
                                 f"{channel_id}/messages?limit=100&before"
                                 f"={before}",
                                 headers=self.headers)
            else:
                r = requests.get(f"https://discord.com/api/v9/channels/"
                                 f"{channel_id}/messages?limit=100",
                                 headers=self.headers)

            no_messages += 100
            result = json.loads(r.content)

            # When we reach the end of the channel we'll get no results
            # signaling a break
            if len(result) == 0:
                break

            before = result[-1]["id"]

            messages.append(result)

        return messages

    def get_links(self, channel_id: str) -> List[Dict[str, str]]:
        """
        Get all links from a Discord channel.
        """
        messages = self.get_messages(channel_id=channel_id)
        return self.extract_links(messages=messages)

    @staticmethod
    def extract_links(messages) -> List[Dict[str, str]]:
        """
        Go through jsons returned by Discord and extract links, as well as
        other metadata.
        """

        links = []
        for i in messages:
            for j in i:
                re_obj = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+',
                                    str(j["content"]))
                if re_obj:
                    for k in re_obj:
                        links.append({"Link": k,
                                      "User": j['author']['username'],
                                      "Date Suggested": j['timestamp']})

        return links
