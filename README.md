# GET_alarm.py

Script that sends a GET request to a specified URL at times in a provided list of timestamps

GET requests are sent with an accuracy down to the second

Assumes times given are for current date, and ignores any times earlier than the present

For intended results, script should be set to run at 00:00 on the desired dates

**NOTE**: This script simply sends a GET request and does nothing with the response;
to tailor the script to your particular usecase, edit the GET_request() function on line 107

## Configuration

The provided `config.ini` contains three configuration options:

1. `URL` : the URL on which to make the GET request
2. `CSV` : the path to a CSV file whose first line is a comma-separated list of desired timestamps
  + the expected format is "hours:minutes:seconds" (zero-padded)
  + an example CSV file is available in this directory
3. `LOG` : the desired path to a logfile, which will be created or opened in append mode

## Running

Requires Python3, no external dependencies

1. Ensure `getalarm.py` and `config.ini` are present in the same directory
2. Launch a shell in that directory and call python on `getalarm.py`

For example:

`$ python getalarm.py`

**NOTE**: on some platforms, the default command is `python3`, not `python`

## Optional Command Line Arguments

Command line arguments can be used to override an existing `config.ini` file:

+ `--url=` or `-u=` : overrides `URL`
+ `--csv=` or `-c=` : overrides `CSV`
+ `--log=` or `-l=` : overrides `LOG`

You can also directly provide the list of timestamps on the command line using:

+ `--timestamps=` or `-t=` : overrides `CSV`

**NOTE**: if there are duplicated or conflicting arguments, the last one given will be used
