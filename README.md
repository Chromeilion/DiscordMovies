# discordmovies
A script that goes through a discord channel with movie links in it. It extracts 
the links from discord, gets metadata for each movie, and creates a Google 
Sheets file or CSV file.

Useful if you run movie nights where people request stuff through discord, and 
would like to automate the process of collecting requests.

## What exactly can discordmovies do?
- Pull all movies from a Discord channel and put them into a CSV or Google Sheet
- Get metadata for each movie, including title, genre, who suggested it, when it 
was suggested, rating, etc.
- Append movies to an already existing Google Sheet or CSV, as well as update
existing values.
- Remove movies that are not present in Discord from an already existant Google 
Sheets
- Format Google Sheets so that images are rendered nicely and headers are sized 
correctly
- Keep track of what you've watched
- Nearly all command-line arguments can also be passed as environment variables
- Let you choose what attributes you want to see with either an include or 
exclude list.
<details>
<summary>What does it look like?</summary>
<br>
<img src="https://imgur.com/RHFrvoT.png" alt="Image of discordmovies sheet.">
</details>

## What can discordmovies not do?
- discordmovies does not monitor a Discord channel. When its done with its 
tasks, it closes and needs to be run again if you wish to update your movies 
file
- Only IMDB, MAL, and Anilist links are supported.
- The program needs certain API keys and credentials to function, it does not 
work out of the box
- discordmovies cannot do any kind of channel moderation. It'll tell you when a 
link is invalid but will not take any action against it apart from ignoring it

## User Guide
As a user, discordmovies is very easy to utilize. All you have to do is send a 
supported link in the movies discord channel, and it'll pop up in the 
spreadsheet the next time discordmovies is run.
If you'd like to mark a film as watched, simply send the same link thats in the 
suggestions channel into the watched channel. The next time discordmovies is 
run, the film will be marked as watched. 

## How can I host discordmovies myself?
Any machine that runs python 3.8 can run discordmovies.
I recommend setting up discordmovies on a server and having it run periodically 
using something like cron job. That being said, if you just want to run it once
off, running it on a regular PC is not an issue.

Nearly all settings can be set through environment variables, therefore, 
instead of using command line arguments, I highly recommend a .env file in the 
program root directory.

Please refer to the setting up section of this readme to see how to get
everything needed working.

### Using Heroku
Because discordmovies runs as a script, it uses up basically zero dyno hours, 
meaning it can be hosted for free on [Heroku](https://www.heroku.com).

In order to host discordmovies on Heroku, all you have to do is fork this 
repository and link a dyno to your new github fork. Then you just use a 
scheduler addon to have discordmovies run whenever you want.

All necessary settings can be set as environment variables in the dyno 
dashboard.

# Setting up
## Google Sheets
If you want to generate a Google Sheets document, you'll need to set up some 
Google API keys.
For this you need to:
1. Create a Google Cloud Platform project 
[here](https://console.cloud.google.com/)
2. Enable the Google Sheets API on the project (APIs & Services > Library)
3. Configure an OAuth consent screen (APIs & Services > OAuth consent screen)
4. Create OAuth client ID (APIs & Services > Credentials > Create Credentials > 
OAuth client ID)
5. Download the credentials file and rename it to credentials.json. Put it into 
the project root directory.

After this you should be set up. When running the program it will ask for access 
to your Google Sheets and create a token.json file with your specific user 
token. 

If you'd like to use environment variables, simply copy-paste the
contents from these files into a .env file with the correct variable names.

## TMDB API Key
In order to get metadata, the program needs a TMDB API key. This can be found 
[here](https://developers.themoviedb.org/3/getting-started/introduction).
The key can be passed as an environment variable or as a command line argument.

## Optional .env
if you'd like to use a .env file instead of keeping keys as files and passing 
arguments through command line, this is possible.
Take a look at [env.example](./env.example) to see everything that can be set.

An important note, when using an env file for your Google app credentials, the 
generated Google user token will be saved to your .env file and then loaded from 
there in future runs instead of being saved to its own file.

# Discord Auth
In order to be able to access Discord, the program needs an authorization token. 
This could either be a Discord bot token (the official way to do it) or a 
Discord user token (the bannable way to do it).

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
Python 3.8 is the only officially supported version, however it'll probably run 
fine on other versions.

There are a few ways to specify what the program should do. I recommend 
running ```python DiscordMovies.py --help``` to see the options.
All options can also be set as environment variables. 

# Supported Link Types
The program currently supports links from IMDB, MAL, and Anilist. Since these 
sources cover pretty much all movies people may want to suggest,
support for more sites will probably not be added. On that note, if you've got 
a reason why you want a site supported, feel free to open an issue.


# Advanced Stuff
While the program produces good-looking spreadsheets by default, if you'd like 
more control, you can use discordmovies in your own script by importing it.

Feel free to have a look around the source code, most of it shouldn't be hard
to understand. I've tried to make certain portions of the code modular, so
adding support for new output types for example is something that isn't hard 
to do.

# Contributing
Anybody is welcome to contribute. Simply fork the repo and make a pull request.
