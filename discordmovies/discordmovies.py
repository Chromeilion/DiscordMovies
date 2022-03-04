from typing import Union
from discordmovies.attributes import DiscordMoviesAttributes
from typing import List
from discordmovies.outputmodules.filehelper import FileHelper
from discordmovies.inputmodules.input import Input


class DiscordMovies:
    """
    A class for going through a discord movie recommendations channel and
    extracting all links. These links can then be uploaded to Google Sheets
    or exported to a CSV.
    """

    def __init__(self, discord_auth_token: Union[str, int], bot: bool = True,
                 doc_name: str = "discordmovies", attributes: List[str] = None,
                 exclude_attributes: List[str] = None):
        self.auth_token = discord_auth_token
        self.bot = bot
        self.attributes = DiscordMoviesAttributes(
            name=doc_name,
            attributes=attributes,
            exclude_attributes=exclude_attributes
        )

    def discord_to_file(self, filetype: str,
                        channel_id: Union[str, int],
                        watched_channel_id: Union[str, int] = None,
                        sheet_id: Union[str, int] = None,
                        max_messages: int = 100,
                        tmdb_api_key: str = None,
                        remove_watched: bool = False,
                        reformat_sheet: bool = False,
                        source: str = "discord"):
        """
        Extract all movies from a Discord channel and save them to a Google
        Sheet or CSV.
        """

        file = FileHelper(filetype=filetype, attributes=self.attributes,
                          sheet_id=sheet_id, reformat_sheet=reformat_sheet)

        current_content = file.get_values()
        # These next few if statements are checking the formatting of the
        # file. Basically if the header is not what's expected, the whole
        # sheet is overwritten.
        if current_content:
            if current_content[0] != self.attributes.movie_list. \
                    get_categories():
                print("File formatting does not match current formatting "
                      "settings. Sheet will be completely rewritten.")
                current_content = []
                overwrite = True
            else:
                overwrite = False
        else:
            overwrite = False

        inputs = Input(
            source_type=source,
            current_content=current_content,
            attributes=self.attributes,
            auth=self.auth_token,
            bot=self.bot,
            tmdb_api_key=tmdb_api_key,
            watched_channel_id=watched_channel_id,
            remove_watched=remove_watched,
            movie_channel_id=channel_id,
            max_messages=max_messages
        )

        if file.exists():
            if not self.attributes.movie_list:
                inputs.setup_movie_list()
            file.write_existing(overwrite=overwrite)
        else:
            if not self.attributes.movie_list:
                inputs.setup_movie_list()
            file.write_new()
