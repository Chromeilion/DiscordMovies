import os
import discordmovies
import argparse
from dotenv import load_dotenv

parser = argparse.ArgumentParser(prog='DiscordMovies',
                                 description='Extract links from a discord '
                                             'channel')

parser.add_argument('--output', action='store', type=str,
                    help='Links can be saved either to a CSV file or to a '
                         'Google Sheet.',
                    choices=["sheet", "csv", "all"])

parser.add_argument('--token', action='store', type=str,
                    help='Token used for authentication with Discords servers.')

parser.add_argument('--google-sheets-id', action='store', type=str,
                    help='The ID of an existing Google Sheets file if you '
                         'want to use one.')

parser.add_argument('--channel-id', action='store', type=str,
                    help='The ID of an existing Google Sheets file if you '
                         'want to use one.')

parser.add_argument('--filename', action='store', type=str,
                    help='The name to be used when creating a Google Sheet or '
                         'CSV file.',
                    default="DiscordMovies")

parser.add_argument('--max-messages', action='store', type=int,
                    help='The maximum amount of messages to download. Doing a '
                         'large amount may result in rate limiting.',
                    default=100)

parser.add_argument('--no-bot', action='store_true',
                    help='Use if token is not a bot token.')

args = parser.parse_args()

load_dotenv()

if not args.output:
    if "OUTPUT_TYPE" in os.environ:
        output = os.environ["OUTPUT_TYPE"]
        if output not in ["sheet", "csv", "all"]:
            raise TypeError('Output type was not correctly specified. Please '
                            'choose from "sheet", "csv", or "all".')
        print("Output type loaded from environment.")
    else:
        raise TypeError('Please specify an output type.')
else:
    output = args.output
    if not output:
        raise TypeError("Output must be specified either as an argument or in "
                        "environment.")

if not args.token:
    from dotenv import load_dotenv

    load_dotenv()
    if "DISCORD_AUTH_TOKEN" in os.environ:
        token = os.environ["DISCORD_AUTH_TOKEN"]
        print("Discord token loaded from environment.")
    else:
        raise TypeError('No Discord auth token found. Please either pass one '
                        'as an argument or have "DISCORD_AUTH_TOKEN" set in '
                        'your environment or within a .env file within this '
                        'directory.')
else:
    token = args.token

if not args.channel_id:
    if "DISCORD_CHANNEL_ID" in os.environ:
        channel_id = os.environ["DISCORD_CHANNEL_ID"]
        print("Channel ID loaded from environment.")
    else:
        raise TypeError('Discord channel ID not found. Please pass it as an '
                        'argument or set as "DISCORD_CHANNEL_ID" in your '
                        'environment or in a .env file within this directory.')
else:
    channel_id = args.channel_id

if not args.google_sheets_id and args.output == "sheets":
    if "GOOGLE_SHEETS_ID" in os.environ:
        sheet_id = os.environ["GOOGLE_SHEETS_ID"]
        print("Google Sheets ID loaded from environment.")
    else:
        print('Google sheets ID not passed and not found in environment. A '
              'new file will be created with the name "DiscordMovies".')
        sheet_id = None
else:
    sheet_id = args.google_sheets_id

if args.no_bot:
    bot = False
else:
    bot = True

filename = args.filename
max_messages = args.max_messages

if output == "sheet" or output == "all":
    discordmovies.DiscordMovies(discord_auth_token=token,
                                bot=bot).discord_to_sheets(
        channel_id=channel_id,
        sheet_id=sheet_id,
        sheet_name=filename,
        max_messages=max_messages)

if output == "csv" or output == "all":
    discordmovies.DiscordMovies(discord_auth_token=token,
                                bot=bot).discord_to_csv(
        channel_id=channel_id,
        csv_name=filename,
        max_messages=max_messages)
