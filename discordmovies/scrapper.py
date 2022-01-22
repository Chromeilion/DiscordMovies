import requests
import json
from typing import Union


class Scrapper:
    """
    A class for handling scrapping from websites. Currently, only messages
    from Discord.
    """

    def __init__(self, auth: Union[int, str]):
        self.auth_token = auth
        self.headers = {
            "authorization": self.auth_token,
        }

    def get_messages(self, channel_id: Union[int, str],
                     max_messages: int = 100) -> list:
        """
        Get all messages from a channel as a list of dictionaries.
        """

        messages = []
        no_messages = 0
        before = None
        # Discord only lets us collect 100 messages at a time, so to get all
        # of them we need to send a couple requests.
        while no_messages < max_messages:
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
