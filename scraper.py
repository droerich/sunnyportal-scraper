#!/usr/bin/env python3

import argparse
import datetime
import json
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


def get_energy_chart(session: requests.Session, headers, start: datetime.datetime, end: datetime.datetime):
    url = 'https://www.sunnyportal.com/FixedPages/HoManEnergyRedesign.aspx'
    resp = session.get(url, headers=headers)
    if not resp.ok:
        return None
    else:
        print("Get HomManEnergyRedesign OK")

    # Get chart without time span
    #   Apparently, this is necessary for the nex request to work as expected
    url = 'https://www.sunnyportal.com/PortalCharts/Core/PortalChartsAPI.aspx'
    params = {
        'id': 'mainChart',
        't': int(time.time() * 1000)
    }
    resp = session.get(url, params=params, headers=headers)
    if not resp.ok:
        return None
    else:
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
    resp = session.get(url, params=params, headers=headers)
    if not resp.ok:
        return None
    else:
        print("Get Energy Chart OK")

    # Download energy data in CSV format
    url = 'https://www.sunnyportal.com/Templates/DownloadDiagram.aspx'
    params = {
        'down': 'homanEnergyRedesign',
        'chartId': 'mainChart'
    }
    resp = session.get(url, params=params, headers=headers)
    if resp.ok:
        print(resp.text)
        pass
    else:
        print("Could not download CSV")


def main():
    cli_parser = argparse.ArgumentParser(
        description="Retrieve energy data from SMA Sunny Portal")
    cli_parser.add_argument('--config', type=str,
                            help="Path to config file", default='.config.json')
    cli_parser.add_argument('-c', '--current', action='store_true',
                            help='Print the current energy generation and consumption')
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
    cet_tz = ZoneInfo("Europe/Berlin")

    session = login(username, password, headers)
    if cli_args.current:
        print_dashboard_info(session, headers)
    else:
        get_energy_chart(session, headers, datetime.datetime(
            2023, 1, 1, 0, 0, tzinfo=cet_tz), datetime.datetime(2023, 1, 2, 0, 0, tzinfo=cet_tz))


if __name__ == "__main__":
    main()
