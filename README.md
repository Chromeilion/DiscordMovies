# discordmovies
A script that goes through a discord channel with movie links in it. It extracts the links from discord, gets metadata for each movie, and creates a Google Sheets file or CSV file.

Useful if you run movie nights where people request stuff through discord, and would like to automate the process of collecting requests.

While the program currently has most necessary features, there's still a lot of polish to be done. Specifically:
- Check if link is actually to a movie site
- General code quality
- A progress bar
- Avoid unnecessary API calls by removing entries already present within an existant CSV/sheet before extracting metadata

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

## TMDB API Key
In order to get metadata, the program needs a TMDB API key. This can be found [here](https://developers.themoviedb.org/3/getting-started/introduction).
The key can be passed as an environment variable or as a command line argument.

## Optional .env
if you'd like to use a .env file instead of keeping all the keys in different files, just copy-paste the contents from credentials.json into the .env file. The variable name is "GOOGLE_APP_CREDENTIALS" and the json contents should be surrounded in single quotes. After adding it to .env, either remove credentials.json or rename it.

When running the program, the generated Google user token will be saved to your .env file and then loaded from there in future runs.


# Discord Auth
In order to be able to access Discord, the program needs an authorization token. This could either be a Discord bot token (the official way to do it) or a Discord user token (the bannable way to do it).

If you'd like to use a user token, pass ```--no-bot``` when running the program.

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
All options can also be set as environment variables. Take a look at env.example to see what variables can be set.

# Contributing
Anybody is welcome to contribute. Simply fork the repo and make a pull request.
