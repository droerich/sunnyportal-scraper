# sunnyportal-scraper
Download energy data from SMA's Sunny Portal

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
