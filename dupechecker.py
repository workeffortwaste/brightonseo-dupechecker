# DupeChecker
# Use the Google Analytics Reporting API to hunt for duplicate transactions

# Installation
# git clone https://github.com/workeffortwaste/brightonseo-dupechecker/
# cd brightonseo-dupechecker
# python3 -m venv env
# source env/bin/activate
# pip install -r requirements.txt

# 1. Ensure your analytics_auth.json file is in the directory.
# 2. Ensure the service account has been added to any Analytics views you wish to use.
# https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/service-py

# Import the Google Analytics API
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import json


# A simple class for the duplicate transaction checker.
class DupeChecker(object):
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
        self.KEY_FILE_LOCATION = 'analytics_auth.json'
        self.VIEW_ID = None

    @staticmethod
    def _output(result: bool):
        # Return basic output as a JSON object
        output = {'result': result}
        return json.dumps(output)

    def report(self, viewid, startdate, enddate):
        self.VIEW_ID = viewid

        analytics = self._initialize_analyticsreporting()
        response = self._get_report(analytics, startdate, enddate)

        output = False  # Default state, no duplicate transactions found
        if response['reports'][0]['data']['totals'][0]['values'][0] != '0':
            if int(response['reports'][0]['data']['rows'][0]['metrics'][0]['values'][0]) > 1:
                output = True  # Duplicate transactions found

        return self._output(output)

    def _get_report(self, analytics, startdate, enddate):
        # Query the Analytics Reporting API V4.
        return analytics.reports().batchGet(
            body={
                'reportRequests': [
                    {
                        'viewId': self.VIEW_ID,
                        'dateRanges': [{'startDate': startdate, 'endDate': enddate}],
                        'metrics': [{'expression': 'ga:transactions'}],
                        'dimensions': [{'name': 'ga:transactionId'}],
                        'pageSize': 1,
                        'orderBys': [{'fieldName': 'ga:transactions', 'sortOrder': 'DESCENDING'}]
                    }
                ]
            }
        ).execute()

    def _initialize_analyticsreporting(self):
        # Initialise an Analytics Reporting API V4 service object.
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.KEY_FILE_LOCATION, self.SCOPES)

        # Build the service object.
        return build('analyticsreporting', 'v4', credentials=credentials, cache_discovery=False)


# Example Usage
# DupeChecker().report('ANALYTICS_VIEW_ID','START_DATE','END_DATE')
print(DupeChecker().report('123456789', '2020-01-01', '2020-09-09'))

