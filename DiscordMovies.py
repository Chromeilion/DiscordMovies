import os
import discordmovies
import argparse
from dotenv import load_dotenv
import ast

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

parser.add_argument('--watched-channel-id', action='store', type=str,
                    help='The ID of the channel where links to watched movies'
                         'are sent.',
                    default=None)

parser.add_argument('--remove-watched', action='store_true',
                    help='Whether or not to remove watched movies from the '
                         'file. Only works if --watched-channel-id is set.',
                    default=False)

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

parser.add_argument('--tmdb-api-key', action='store_true',
                    help='An API key for The Movie Database')

parser.add_argument('--reformat-sheet', action='store_true',
                    help='Whether the Google Sheet should be reformatted. This'
                         'action creates a lot of writes so should not be left'
                         'on by default.',
                    default=False)

parser.add_argument('--attributes', action='store',
                    help='What attributes each movie should have. Things like'
                         'User Score, Genres and Runtime. By default will have'
                         'all available attributes. Takes a list of strings.',
                    default=None)

parser.add_argument('--exclude-attributes', action='store',
                    help='What attributes should be excluded from the sheet.'
                         'Takes a list of strings.',
                    default=None)

args = parser.parse_args()

load_dotenv()

sheet_outs = ["sheet", "all"]
csv_outs = ["csv", "all"]

if args.output is None:
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

if args.google_sheets_id is None and output in sheet_outs:
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

if not args.tmdb_api_key:
    if "TMDB_API_KEY" in os.environ:
        tmdb_api_key = os.environ["TMDB_API_KEY"]
        print("TMDB API key type loaded from environment.")
    else:
        print("No TMDB API key detected. Continuing without it. There may be "
              "some data missing.")
        tmdb_api_key = None
else:
    tmdb_api_key = args.tmdb_api_key

if not args.watched_channel_id:
    if "WATCHED_CHANNEL_ID" in os.environ:
        watched_channel_id = os.environ["WATCHED_CHANNEL_ID"]
        print("Watched channel ID loaded from environment.")
    else:
        print("No watched channel ID found, continuing without it.")
        watched_channel_id = None
else:
    watched_channel_id = args.watched_channel_id

if not args.remove_watched:
    if "REMOVE_WATCHED" in os.environ:
        remove_watched = os.environ["REMOVE_WATCHED"]
        remove_watched = ast.literal_eval(remove_watched)
    else:
        remove_watched = False
else:
    remove_watched = True
if remove_watched:
    print("Watched movies will be removed.")

if not args.reformat_sheet:
    if "REFORMAT_SHEET" in os.environ:
        reformat_sheet = os.environ["REFORMAT_SHEET"]
        reformat_sheet = ast.literal_eval(reformat_sheet)
    else:
        reformat_sheet = False
else:
    reformat_sheet = True

if args.attributes is None:
    if "ATTRIBUTES" in os.environ:
        attributes = os.environ["ATTRIBUTES"]
        attributes = ast.literal_eval(attributes)
    else:
        attributes = args.attributes
else:
    attributes = ast.literal_eval(args.attributes)

if args.exclude_attributes is None:
    if "EXCLUDE_ATTRIBUTES" in os.environ:
        exclude_attributes = os.environ["EXCLUDE_ATTRIBUTES"]
        exclude_attributes = ast.literal_eval(exclude_attributes)
    else:
        exclude_attributes = args.attributes
else:
    exclude_attributes = ast.literal_eval(args.exclude_attributes)

if remove_watched:
    print("Watched movies will be removed.")

filename = args.filename
max_messages = args.max_messages

output_types = []
if output in sheet_outs:
    output_types.append("sheet")
if output in csv_outs:
    output_types.append("csv")

for i in output_types:
    discordmovies.DiscordMovies(
        discord_auth_token=token,
        bot=bot,
        doc_name=filename,
        attributes=attributes,
        exclude_attributes=exclude_attributes
    ).discord_to_file(
        channel_id=channel_id,
        watched_channel_id=watched_channel_id,
        sheet_id=sheet_id,
        max_messages=max_messages,
        tmdb_api_key=tmdb_api_key,
        filetype=i,
        remove_watched=remove_watched,
        reformat_sheet=reformat_sheet
    )
