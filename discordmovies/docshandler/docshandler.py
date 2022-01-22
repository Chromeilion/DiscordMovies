import googleapiclient.errors
from googleapiclient.discovery import build
from .credentials import Creds


class DocsHandler:
    """
    A class that deals with the Google Docs API.
    """

    def __init__(self, spreadsheet_id: str = None):
        self.creds = Creds()
        self.service = None
        self.spreadsheet_id = spreadsheet_id

    def set_spreadsheet_id(self, spreadsheet_id: str):
        """
        If you want to change the spreadsheet ID that was set initially, use
        this method to change it.
        """

        self.spreadsheet_id = spreadsheet_id

    def setup_docs(self):
        """
        Attempts to set up variables necessary for the functioning of the class.
        """

        self.creds.setup_creds()
        self.creds.check_creds()
        self.service = build("sheets", "v4", credentials=self.creds.creds)

    def get_doc_contents(self) -> dict:
        """
        Get all contents from a spreadsheet in the form of a dictionary.
        """

        return self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range="A:Z").execute()

    def create_sheet(self, title: str):
        """
        Create an empty Google Docs sheet and set the title. Also updates the
        spreadsheet id.
        """

        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        spreadsheet = self.service.spreadsheets().create(body=spreadsheet,
                                                         fields='spreadsheetId'
                                                         ).execute()
        self.spreadsheet_id = spreadsheet.get('spreadsheetId')

        print('Spreadsheet created successfully.')

    def fill_sheet(self, inputs: list):
        """
        Inserts contents into the body of a sheet. Input should be a list
        of lists with each list being a row.
        """
        data = [
            {"range": "A:Z",
             "values": inputs}
        ]
        body = {
            'valueInputOption': "RAW",
            'data': data
        }
        result = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=self.spreadsheet_id, body=body).execute()
        print('{0} cells updated '.format(result.get('totalUpdatedCells')))

    def check_existence(self, sheet_id: str = None) -> bool:
        """
        Check if a document exists by sending a request for it. Returns false
        if an error is returned.
        """

        if sheet_id is None:
            sheet_id = self.spreadsheet_id

        if self.spreadsheet_id is None:
            return False

        try:
            self.service.spreadsheets().get(
                spreadsheetId=sheet_id).execute()
        except googleapiclient.errors.HttpError:
            return False
        return True

    def append_sheet(self, values):
        body = {
            'values': values
        }
        result = self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id, range="A:Z",
            valueInputOption="RAW", body=body).execute()
        print('{0} cells appended.'.format(result
                                           .get('updates')
                                           .get('updatedCells')))
