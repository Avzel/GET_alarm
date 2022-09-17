import configparser
import logging
import sys
from datetime import datetime
from io import StringIO, TextIOWrapper
from threading import Timer
from typing import Tuple, Union
from urllib.request import urlopen


format = '%H:%M:%S'

def parse_config(configfile: str) -> Tuple[str, str, str]:
    '''
    Parses config file and returns its contents

    ------
    Returns:
        Tuple[url: str, csv: str, log: str]
    '''

    config = configparser.ConfigParser()
    config.read(configfile)

    url = config['DEFAULT']['URL']
    csv = config['DEFAULT']['CSV']
    log = config['DEFAULT']['LOG']
    
    return (url, csv, log)

def get_inputs(configfile: str) -> Tuple[str, str]:
    '''
    Returns request URL and timestamps CSV, also sets global logger
    If conflicting or duplicated args, uses last provided

    ------
    Returns:
        Tuple[url: str, csv: str]
    '''

    url, csv, log = parse_config(configfile)

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            index = arg.find('=') + 1
            if len(arg) > index and any(arg.startswith(x) for x in ('-u=', '--url=')):
                url = arg[index:]
            elif len(arg) > index and any(arg.startswith(x) for x in ('-c=', '-t=', '--csv=', '--timestamps=')):
                csv = arg[index:]
            elif len(arg) > index and any(arg.startswith(x) for x in ('-l=', '--log=')):
                log = arg[index:]
            else:
                sys.exit('Invalid command line arguments')

    logging.basicConfig(filename=log, level=logging.INFO)
    
    return (url, csv)

def get_fileobject(csv: str) -> Union[TextIOWrapper, StringIO]:
    '''
    Returns appropriate python IO object depending on contents of given var 'csv'
    
    -------
    Returns:
        TextIOWrapper -> if 'csv' contains path to CSV file
        StringIO -> otherwise
    '''

    if csv.endswith('.csv'):
        return open(csv)
    else:
        return StringIO(csv)

def parse_timestamps(csv: str) -> list:
    '''
    Returns list of datetime objects parsed from given var 'csv'
    '''

    file = get_fileobject(csv)
    timestamps = file.readline().split(',')

    for index, timestamp in enumerate(timestamps):
        try:
            timestamps[index] = datetime.strptime(timestamp, format).replace(
                day=datetime.today().day,
                month=datetime.today().month,
                year=datetime.today().year
                )
        except ValueError:
            logging.error(f'({datetime.now()}) Invalid timestamp ignored ({timestamp})')
            print(f'Invalid time stamp ignored ({timestamp})')
            timestamps.pop(index)

    if not timestamps:
        logging.critical(f'({datetime.now()}) Terminated due to no valid timestamps')
        sys.exit('No valid timestamps; terminating...')

    return timestamps

def GET_request(url: str) -> None:
    '''
    Performs GET request to given URL
    '''

    try:
        with urlopen(url) as response:
            logging.info(f'({datetime.now()}) GET request made to {url}')

            # TODO: Implement your own functionality here using the GET response

            return response.read()

    except ValueError:
        logging.critical(f'({datetime.now()}) Unable to complete GET request due to invalid URL ({url})')
        sys.exit('Invalid URL format')

def launch_GET_handler(url: str, csv: str) -> None:
    '''
    Creates and starts threads to send GET requests at specified times;
    Waits for their execution to complete before returning
    '''

    timestamps = parse_timestamps(csv)

    threads = []

    for timestamp in timestamps:
        delay = (timestamp - datetime.now()).total_seconds()
        if delay < 0:
            continue
        else:
            thread = Timer(delay, GET_request, [url])
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    configfile = 'config.ini'
    url, csv = get_inputs(configfile)
    launch_GET_handler(url, csv)
