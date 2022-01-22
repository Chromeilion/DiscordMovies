# discordmovies
A script that goes through a discord channel, extracts movie links, and creates a google sheets sheet for them or saves them to a CSV.

Usefull if you run movie nights where people request stuff through discord, and would like to automate the process of collecting requests.

# Setting up
If you want to generate a google sheets document, you'll need to set up some Google API keys.
For this you need to:
1. Create a Google Cloud Platform project [here](https://console.cloud.google.com/)
2. Enable the Google Sheets API on the project (APIs & Services > Library)
3. Configure an OAuth consent screen (APIs & Services > OAuth consent screen)
4. Create OAuth client ID (APIs & Services > Credentials > Create Credentials > OAuth client ID)
5. Download the credentials file and rename it to credentials.json. Put it into the poject root directory.
After this you should be set up. When running the program it will ask for access to your drive and create a token.json file with your specific user token.

# Running
To run the program simply run DiscordMovies.py with python. Python 3.8 is the only officially supported version, however it'll probably run fine on other versions.

There are a few ways to specify what the program should do. I recommend running python DiscordMovies.py --help to see the options.
All options except 
