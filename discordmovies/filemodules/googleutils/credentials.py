import json
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError


class Creds:
    """
    Handles Google Docs credentials and scopes. Can be used to load credentials
    from a file, save them to a file, to renew them, and to verify their
    integrity.
    """

    def __init__(self, creds=None):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.creds = creds

    def check_creds(self) -> bool:
        """
        Checks credentials. If they are invalid, recommends an action to
        the user and raises a ValueError. If they are valid returns True.
        """

        if not self.creds:
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json',
                                                              self.SCOPES)

                if not creds.valid:
                    raise ValueError("token.json found, but credentials "
                                     "are invalid. Try running setup_creds "
                                     "to attempt to renew them.")
                return True
            elif "GOOGLE_USER_CREDENTIALS" in os.environ:
                creds_env = os.environ["GOOGLE_USER_CREDENTIALS"]
                creds_env = json.loads(creds_env)
                creds = Credentials.from_authorized_user_info(creds_env)

                if creds.expired:
                    raise ValueError("User credentials found in environment,"
                                     "however they are expired. Please"
                                     "try running setup_creds to renew them.")
                if not creds.valid:
                    raise ValueError("User credentials found in environment,"
                                     "however they are not valid. Either"
                                     "try running setup_creds to renew them,"
                                     "or try recreating them.")
            else:
                raise ValueError("Credentials not found. Please either "
                                 "pass them to the function, or place a "
                                 "token.json in the root project "
                                 "directory. For information on how to "
                                 "get credentials see README.md")
        if not self.creds.valid:
            raise ValueError("Credentials are invalid, please run "
                             "setup_creds to try and set them up.")
        return True

    def setup_creds(self):
        """
        Attempts to load credentials from a token.json file. If the file is
        not found, attempts to create them using credentials.json. If
        credentials.json is not found, a FileNotFoundError is raised.
        """

        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json',
                                                               self.SCOPES)
        elif "GOOGLE_USER_CREDENTIALS" in os.environ:
            creds_env = json.loads(os.environ["GOOGLE_USER_CREDENTIALS"])
            self.creds = Credentials.from_authorized_user_info(creds_env)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except RefreshError as e:
                    raise RefreshError("Unable to refresh user token. Try "
                                       "deleting the user token and then "
                                       "recreating it. This could be caused "
                                       "by having the Google project OAuth "
                                       "publishing status set to 'testing' "
                                       "try setting it to 'in production', "
                                       "this makes it so that tokens don't "
                                       "expire.") from e

            else:
                if os.path.exists('credentials.json'):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', self.SCOPES)

                    self.creds = flow.run_local_server(port=0)

                    # Save the credentials for the next run
                    with open('token.json', 'w') as token:
                        token.write(self.creds.to_json())
                    print("Credentials have been renewed and saved to "
                          "token.json")

                elif "GOOGLE_APP_CREDENTIALS" in os.environ:
                    flow = InstalledAppFlow.from_client_config(
                        json.loads(
                            os.environ["GOOGLE_APP_CREDENTIALS"]),
                        self.SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)

                    from dotenv import find_dotenv, set_key

                    # Save credentials to environment for the next run
                    user_creds = self.creds.to_json()
                    os.environ["GOOGLE_USER_CREDENTIALS"] = user_creds
                    file = find_dotenv()

                    if not file:
                        # Save the credentials to a file
                        with open('token.json', 'w') as token:
                            token.write(user_creds)
                        print("Credentials have been renewed. No .env file "
                              "was found, so they were saved to token.json")
                    else:
                        # Save credentials to .env file
                        set_key(file, "GOOGLE_USER_CREDENTIALS",
                                user_creds)
                        print('Credentials have been renewed and saved to '
                              '.env file')

                else:
                    raise FileNotFoundError("the Google user token is invalid "
                                            "and credentials.json has not "
                                            "been found. Therefore, it is "
                                            "impossible to generate a user "
                                            "token. Please set up "
                                            "credentials.json in order to "
                                            "generate a new user token.")
