import GET_alarm
import logging
import os
import unittest
from datetime import datetime, timedelta
from io import StringIO, TextIOWrapper
from unittest.mock import patch


class GET_Alarm_Test(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        '''
        Sets instance variables for easy access in all tests
        '''
        
        super(GET_Alarm_Test, self).__init__(*args, **kwargs)
        self._test_url = 'https://google.com'
        self._test_ini = 'GET_Alarm_Test.ini'
        self._test_csv = 'GET_Alarm_Test.csv'
        self._test_log = 'GET_Alarm_Test.txt'

    def setUp(self):
        '''
        Creates custom test files before each test
        '''

        with open(self._test_ini, 'w') as file:
            file.writelines([
                '[DEFAULT]\n', 
                f'URL={self._test_url}\n',
                f'CSV={self._test_csv}\n',
                f'LOG={self._test_log}\n'
                ])

        for filename in (self._test_csv, self._test_log):
            with open(filename, 'w') as file:
                file.write('')

    def tearDown(self):
        '''
        Deletes custom test files after each test
        Resets the root logger
        '''

        os.remove(self._test_ini)
        os.remove(self._test_csv)
        os.remove(self._test_log)

        logging.basicConfig(force=True)

    def generate_timestamps(self) -> str:
        '''
        Produces comma-separated timestamps 5 and 10 seconds from present
        
        ------
        Returns:
            str -> comma-separated timestamps
        '''

        soon = datetime.now() + timedelta(seconds=10)
        sooner = datetime.now() + timedelta(seconds=5)
        return f'{soon.strftime(GET_alarm.format)},{sooner.strftime(GET_alarm.format)}'

    def test_parse_config(self):
        '''
        Tests that parse_config() successfully reads from the log file on disk
        '''

        url, csv, log = GET_alarm.parse_config(self._test_ini)
        self.assertEqual(url, self._test_url)
        self.assertEqual(csv, self._test_csv)
        self.assertEqual(log, self._test_log)

    def test_get_inputs(self):
        '''
        Tests that command line arguments are properly parsed
        '''

        test_url = 'notaurl'
        test_timestamp = 'notatimestamp'

        with patch('sys.argv', ['GET_alarm.py', f'-u={test_url}', f'--timestamps={test_timestamp}']):
            url, csv = GET_alarm.get_inputs(self._test_ini)
            self.assertEqual(url, test_url)
            self.assertEqual(csv, test_timestamp)

    def test_get_file_object(self):
        '''
        Tests that get_file_object() returns correct type of IO object based on given String
        '''

        test_csv = '01:23:45,67:89:10'
        
        file = GET_alarm.get_fileobject(test_csv)
        self.assertTrue(type(file) == StringIO)
        
        file = GET_alarm.get_fileobject(self._test_csv)
        self.assertTrue(type(file) == TextIOWrapper)

    def test_parse_timestamps(self):
        '''
        Tests that comma-separated timestamps are correctly parsed into list of Datetime objects
        '''

        test_csv = '01:23:45,12:34:56'
        timestamps = GET_alarm.parse_timestamps(test_csv)

        self.assertTrue(len(timestamps) == 2)
        self.assertEqual(timestamps[0].strftime('%H:%M:%S'), test_csv[:8])
        self.assertEqual(timestamps[1].strftime('%H:%M:%S'), test_csv[9:])

    def test_GET_request(self):
        '''
        Tests that a response was successfully received after a GET request
        '''

        body = GET_alarm.GET_request(self._test_url)
        self.assertTrue(body.startswith(b'<!doctype html>'))

    def test_launch_GET_handler(self):
        '''
        Test confirms GET requests are sent at the correct timestamp
        '''

        timestamps = self.generate_timestamps()

        logging.basicConfig(filename=self._test_log, level=logging.INFO)
        GET_alarm.launch_GET_handler(self._test_url, timestamps)

        with open(self._test_log, 'r') as results:
            self.assertEqual(results.readline()[22:30], timestamps[9:])
            self.assertEqual(results.readline()[22:30], timestamps[:8])

    def test_GET_alarm(self):
        '''
        Integration test confirms functions all work properly together
        '''

        timestamps = self.generate_timestamps()

        with patch('sys.argv', ['GET_alarm.py', f'-t={timestamps}']):
            url, csv = GET_alarm.get_inputs(self._test_ini)
            GET_alarm.launch_GET_handler(url, csv)

        with open(self._test_log, 'r') as results:
            self.assertEqual(results.readline()[22:30], timestamps[9:])
            self.assertEqual(results.readline()[22:30], timestamps[:8])

if __name__ == '__main__':
    unittest.main()
