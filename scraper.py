#!/usr/bin/env python3

import argparse
import datetime
import json
import os
import requests
import time
from zoneinfo import ZoneInfo


def login(username: str, password: str, headers) -> requests.Session:
    url = 'https://www.sunnyportal.com/Templates/Start.aspx?logout=true'
    form_data = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "ctl00$ContentPlaceHolder1$Logincontrol1$txtUserName": username,
        "ctl00$ContentPlaceHolder1$Logincontrol1$txtPassword": password,
        "ctl00$ContentPlaceHolder1$Logincontrol1$LoginBtn": "Anmelden",
        "ctl00$ContentPlaceHolder1$Logincontrol1$ServiceAccess": "true",
        "ctl00$ContentPlaceHolder1$Logincontrol1$MemorizePassword": "on",
        "ClientBrowserVersion": "95",
        "ClientAppVersion": "5.0+(Windows)",
        "ClientAppName": "Netscape",
        "ClientLanguage": "de",
        "ClientPlatform": "Win32",
        "ClientUserAgent": "Mozilla/5.0+(Windows+NT+10.0;+Win64;+x64;+rv:121.0)+Gecko/20100101+Firefox/121.0",
        "ctl00$ContentPlaceHolder1$hiddenLanguage": "de-de"
    }
    session = requests.Session()
    response = session.post(url, data=form_data, headers=headers)
    if not response.ok:
        raise RuntimeError("Login failed: {}".format(response.text))
    print("Login successful.")
    return session


def print_dashboard_info(session: requests.Session, headers):
    """
    Retrieves and prints the current power generation and consumption.
    """
    dashboard_url = 'https://www.sunnyportal.com/Dashboard'
    # Milliseconds since Unix epoch
    timestamp = int(time.time() * 1000)
    params = {
        't': timestamp
    }
    response = session.get(dashboard_url, params=params, headers=headers)
    if not response.ok:
        print("Could not get Dashboard: {}", response.text)
        return
    dashboard_json = response.json()
    if dashboard_json != None:
        print("Current energy data")
        print("PV generation    : {}W".format(dashboard_json['PV']))
        print("Total consumption: {}W".format(
            dashboard_json['TotalConsumption']))
        print("Grid consumption : {}W".format(
            dashboard_json['GridConsumption']))
    else:
        print("Could not get Dashboard info: No JSON data")


def get_energy_chart(session: requests.Session, headers, start: datetime.datetime, end: datetime.datetime) -> str:
    def sunny_request(url, params=None):
        resp = session.get(url, headers=headers, params=params)
        if not resp.ok:
            raise RuntimeError(
                "Request to {} failed with status {}".format(url, resp.status_code))
        return resp

    sunny_request(
        'https://www.sunnyportal.com/FixedPages/HoManEnergyRedesign.aspx')
    print("Get HomManEnergyRedesign OK")

    # Get chart without time span
    #   Apparently, this is necessary for the nex request to work as expected
    url = 'https://www.sunnyportal.com/PortalCharts/Core/PortalChartsAPI.aspx'
    params = {
        'id': 'mainChart',
        't': int(time.time() * 1000)
    }
    sunny_request(url, params)
    resp = session.get(url, params=params, headers=headers)
    print("Get Energy Chart OK")

    # Get chart with time span
    #   This enables download of a specific range
    url = 'https://www.sunnyportal.com/PortalCharts/Core/PortalChartsAPI.aspx'
    params = {
        'id': 'mainChart',
        'xf': int(start.timestamp()),
        'xt': int(end.timestamp()),
        't': int(time.time() * 1000)
    }
    sunny_request(url, params)
    print("Get Energy Chart OK")

    # Download energy data in CSV format
    url = 'https://www.sunnyportal.com/Templates/DownloadDiagram.aspx'
    params = {
        'down': 'homanEnergyRedesign',
        'chartId': 'mainChart'
    }
    resp = sunny_request(url, params)
    return resp.text


def to_day(date_str: str) -> datetime.datetime:
    """
    Helper function converting a string in format "YYYY-MM-DD" to a datetime object
    """
    return datetime.datetime.strptime(date_str, '%Y-%m-%d')


def current(session, headers, _args):
    """
    Called for CLI subcommand "current". Prints current energy consumption.
    """
    print_dashboard_info(session, headers)


def history(session, headers, args):
    """
    Called with the CLI args for CLI subcommand "history". Retrieves energy data for a given time span.
    """
    cet_tz = ZoneInfo("Europe/Berlin")
    if args.day != None:
        start_date = args.day.replace(
            tzinfo=cet_tz, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = datetime.datetime.now(cet_tz).replace(
            hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + datetime.timedelta(days=1)
    print("Retrieving energy data from {} to {}".format(start_date, end_date))

    try:
        energy_csv = get_energy_chart(session, headers, start_date, end_date)
    except RuntimeError as e:
        print("Error getting energy data: {}".format(e))
        return

    try:
        out_dir = '.'
        if args.out_dir != None:
            out_dir = args.out_dir
            os.makedirs(out_dir, exist_ok=True)
        filename = "sma_energy_data_{}.csv".format(
            datetime.datetime.strftime(start_date, '%Y-%m-%d'))
        out_path = os.path.join(out_dir, filename)
        with open(out_path, 'w') as file:
            file.write(energy_csv)
        print("Energy data written to {}".format(out_path))
    except Exception as e:
        print("Error writing CSV file: {}".format(e))
        return


def main():
    # Create command line parser
    cli_parser = argparse.ArgumentParser(
        description="Retrieve energy data from SMA Sunny Portal")
    cli_parser.add_argument('--config', type=str,
                            help="Path to config file", default='.config.json')
    subparsers = cli_parser.add_subparsers(
        title='subcommand', dest='subcommand', help='Subcommand', required=True)
    #   Subcommand "current"
    current_cmd_parser = subparsers.add_parser(
        'current', help='Print the current energy generation and consumption')
    current_cmd_parser.set_defaults(func=current)
    #   Subcommand "history"
    history_cmd_parser = subparsers.add_parser(
        'history', help='Retrieve historic energy data in CSV format. Without arguments gets data from today.')
    history_cmd_parser.add_argument(
        '--day', '-d', type=to_day, help='The day to retrieve in the format YYYY-MM-DD')
    history_cmd_parser.add_argument(
        '--out-dir', '-o', help='Directory to write the ouput file(s) to')
    history_cmd_parser.set_defaults(func=history)

    # Parse command line arguments
    cli_args = cli_parser.parse_args()

    try:
        with open(cli_args.config, 'r') as config_file:
            config = json.load(config_file)
        username = config['username']
        password = config['password']
    except Exception as e:
        print("Could not parse config file: {}".format(e))
        return

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
    }

    session = login(username, password, headers)
    # Call the function handling the subcommand
    cli_args.func(session, headers, cli_args)


if __name__ == "__main__":
    main()
