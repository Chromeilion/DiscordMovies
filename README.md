# discordmovies
A script that goes through a discord channel, extracts links, and creates a google sheets sheet for them or saves them to a CSV.

Useful if you run movie nights where people request stuff through discord, and would like to automate the process of collecting requests.

The program is currently in a pretty basic state, where all it does is extract links. Some ideas on how to improve it:
- Check if link is actually to a movie site
- Extract movie title from the website linked
- Group links by movie title
- Extract movie art and other metadata from links
- Store names of users who suggested the film

# Setting up
## Google Sheets
If you want to generate a google sheets document, you'll need to set up some Google API keys.
For this you need to:
1. Create a Google Cloud Platform project [here](https://console.cloud.google.com/)
2. Enable the Google Sheets API on the project (APIs & Services > Library)
3. Configure an OAuth consent screen (APIs & Services > OAuth consent screen)
4. Create OAuth client ID (APIs & Services > Credentials > Create Credentials > OAuth client ID)
5. Download the credentials file and rename it to credentials.json. Put it into the poject root directory.

After this you should be set up. When running the program it will ask for access to your Google Sheets and create a token.json file with your specific user token.

## Optional .env
if you'd like to use a .env file instead of keeping all the keys in different files, just copy-paste the contents from credentials.json into the .env file. The variable name is "GOOGLE_APP_CREDENTIALS" and the json contents should be surrounded in single quotes. After adding it to .env, either remove credentials.json or rename it.

When running the program, the generated Google user token will be saved to your .env file and then loaded from there in future runs.


# Discord Auth
In order to be able to access Discord, the program needs an authorization token. This could either be a Discord bot token (the official way to do it) or a Discord user token (the bannable way to do it).

If you'd like to use a user token, pass ```--bot False``` when running the program.

# Running
First make sure to install the dependancies with:
```
pip install -r requirements.txt
```

Then, simply run DiscordMovies.py with python. 
```
python DiscordMovies.py
```
Python 3.8 is the only officially supported version, however it'll probably run fine on other versions.

There are a few ways to specify what the program should do. I recommend running ```python DiscordMovies.py --help``` to see the options.
All options can also be set as environment variables. Take a look at template.env to see what variables can be set.

# Contributing
Anybody is welcome to contribute. Simply fork the repo and make a pull request.
