# discordmovies
A script that goes through a discord channel with movie links in it. It extracts the links from discord, gets metadata for each movie, and creates a Google Sheets file or CSV file.

Useful if you run movie nights where people request stuff through discord, and would like to automate the process of collecting requests.

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
if you'd like to use a .env file instead of keeping keys as files and passing arguments through command line this is possible.
Take a look at env.example to see everything that can be set.

An important note, when using an env file for your Google app credentials, the generated Google user token will be saved to your .env file and then loaded from there in future runs
instead of being saved to a file.


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
All options can also be set as environment variables. 

# Advanced Stuff
While the program produces good-looking spreadsheets by default, if you'd like more control you can use discordmovies in your own script by importing it.
If you'd like to see how discordmovies can be used in a script, just checkout DiscordMovies.py for an example.

Some submodules are quite self-sufficient, like docshandler for example, which could be used in all kinds of contexts when you just need to deal with Google sheets.


# Contributing
Anybody is welcome to contribute. Simply fork the repo and make a pull request.
