import googleapiclient.errors
from googleapiclient.discovery import build
from .credentials import Creds
from typing import List, Tuple


class DocsHandler:
    """
    A class that deals with the Google Docs API.
    """

    def __init__(self, spreadsheet_id: str = None):
        self.creds = Creds()
        self.service = None
        self.spreadsheet_id = spreadsheet_id
        self.spreadsheet_name = "Sheet1"

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
            spreadsheetId=self.spreadsheet_id, range="A:Z",
            valueRenderOption="FORMULA"
        ).execute()

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

    def fill_sheet(self, inputs: List[List[str]]):
        """
        Inserts contents into the body of a sheet. Input should be a list
        of lists with each list being a row.
        """

        data = [
            {"range": "A:Z",
             "values": inputs}
        ]
        body = {
            'valueInputOption': "USER_ENTERED",
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
            print("Sheet ID specified, but not found.")
            return False
        return True

    def append_sheet(self, values: List[List[str]], quiet: bool = False):
        """
        Append a list of values to a sheet.
        """

        body = {
            'values': values
        }
        result = self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id, range="A:Z",
            valueInputOption="USER_ENTERED", body=body).execute()
        if not quiet:
            print('{0} cells appended.'.format(result
                                               .get('updates')
                                               .get('updatedCells')))

    def adjust_row_height(self, height: int, start_row: int = None,
                          end_row: int = None):
        """
        Changes height of all rows in the range between start_row and end_row
        to value given.
        """

        requests = [
            {
                "updateDimensionProperties": {
                    "range": {
                        "dimension": "ROWS",
                        "startIndex": start_row,
                        "endIndex": end_row
                    },
                    "properties": {
                        "pixelSize": height
                    },
                    "fields": "pixelSize"
                }
            }

        ]

        body = {
            'requests': requests
        }

        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=body).execute()

    def set_alignment(self, hor_alignment: str = "CENTER",
                      ver_alignment: str = "MIDDLE", wrap: str = "WRAP"):
        """
        Sets the alignment of all cells in the sheet.
        """

        requests = [
            {
                "repeatCell": {
                    "cell": {
                        "userEnteredFormat": {
                            "verticalAlignment": ver_alignment,
                            "horizontalAlignment": hor_alignment,
                            "wrapStrategy": wrap
                        }
                    },
                    "range": {
                    },
                    "fields": "userEnteredFormat"
                }
            }
        ]

        body = {
            'requests': requests
        }

        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=body).execute()

    def remove_row(self, start: int, stop: int):
        """
        Removes a range of rows in a spreadsheet. To remove one row, make start
        the row you want to remove, and stop the next row.
        """

        requests = [
            {
                "deleteDimension": {
                    "range": {
                        "dimension": "ROWS",
                        "startIndex": start,
                        "endIndex": stop
                    },
                }
            }
        ]

        body = {
            'requests': requests
        }

        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=body).execute()

    def update_value(self, value: List[List[str]], start_index: Tuple[int, int],
                     stop_index):
        """
        Update a cell/range in the sheet given the index and value/s.
        """

        coordinates = self.convert_a1(start_coordinate=start_index,
                                      end_coordinate=stop_index)

        body = {
            "values": value
        }

        request = self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id, range=coordinates,
            valueInputOption="USER_ENTERED", body=body)

        request.execute()

    def freeze_row(self, rows: int = 1):
        """
        Freeze n amount of rows at the top of the sheet.
        """

        requests = [
            {
                "updateSheetProperties": {
                    "properties": {
                        "gridProperties": {
                            "frozenRowCount": rows
                        }
                    },
                    "fields": "gridProperties.frozenRowCount"
                }
            }

        ]

        body = {
            'requests': requests
        }

        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=body).execute()

    def clear_sheet(self):
        """
        Deletes all content in a sheet.
        """

        requests = [
            {
                "updateCells": {
                    "range": {
                    },
                    "fields": "userEnteredValue"
                }
            }

        ]

        body = {
            'requests': requests
        }

        self.service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=body).execute()

    @staticmethod
    def convert_a1(start_coordinate: Tuple[int, int],
                   end_coordinate: Tuple[int, int]) -> str:
        """
        Given numpy style indexes, convert them to Google Sheets A1 notation.
        """

        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        return alphabet[start_coordinate[0]] + str(start_coordinate[1] + 1) + \
            ":" + alphabet[end_coordinate[0]] + str(end_coordinate[1] + 1)
