# sunnyportal-scraper
Download energy data from SMA's Sunny Portal

## Installation
Requires Python 3. A virtual environment (venv) is recommended. To set it up, go to the checkout dir and:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
See [Python doc][1] for more information.

## Configuration
Rename `.config_default.json` to `.config.json` and enter your Sunny Portal username and password.

## Usage
Print current energy generation and consumption:
```
sunny_scrape.py current
```

Get energy data of April 21, 2023 in CSV format:
```
sunny_scrape.py history --day=2023-04-21
```

Get energy data of the complete year 2023, one CSV file per day.
```
sunny_scrape.py history --full-year=2023
```

[1]: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
