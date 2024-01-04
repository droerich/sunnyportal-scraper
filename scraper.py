#!/usr/bin/env python3

import requests
import time
import datetime
import json
from zoneinfo import ZoneInfo

def login(username: str, password: str, headers) -> requests.Session:
    url = 'https://www.sunnyportal.com/Templates/Start.aspx?logout=true'
    form_data = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "ctl00$ContentPlaceHolder1$Logincontrol1$txtUserName": username,
        "ctl00$ContentPlaceHolder1$Logincontrol1$txtPassword": password,
        "ctl00$ContentPlaceHolder1$Logincontrol1$LoginBtn": "Anmelden",
        "ctl00$ContentPlaceHolder1$Logincontrol1$RedirectURL": "",
        "ctl00$ContentPlaceHolder1$Logincontrol1$RedirectPlant": "",
        "ctl00$ContentPlaceHolder1$Logincontrol1$RedirectPage": "",
        "ctl00$ContentPlaceHolder1$Logincontrol1$RedirectDevice": "",
        "ctl00$ContentPlaceHolder1$Logincontrol1$RedirectOther": "",
        "ctl00$ContentPlaceHolder1$Logincontrol1$PlantIdentifier": "",
        "ctl00$ContentPlaceHolder1$Logincontrol1$ServiceAccess": "true",
        "ctl00$ContentPlaceHolder1$Logincontrol1$MemorizePassword": "on",
        "ClientScreenWidth": "1536",
        "ClientScreenHeight": "864",
        "ClientScreenAvailWidth": "1536",
        "ClientScreenAvailHeight": "824",
        "ClientWindowInnerWidth": "1536",
        "ClientWindowInnerHeight": "739",
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
        print("Aktuelle Energiedaten")
        print("PV-Erzeugung: {}W".format(dashboard_json['PV']))
        print("Verbrauch   : {}W".format(dashboard_json['TotalConsumption']))
        print("Netzbezug   : {}W".format(dashboard_json['GridConsumption']))
    else:
        print("Could not get Dashboard info: No JSON data")

def get_energy_chart(session: requests.Session, headers, start: datetime.datetime, end: datetime.datetime):
    url = 'https://www.sunnyportal.com/FixedPages/HoManEnergyRedesign.aspx'
    resp = session.get(url, headers=headers)
    if not resp.ok:
        return None
    else:
        print("Get HomManEnergyRedesign OK")

    # Chart OHNE Zeitparameter
    # Offensichtlich ist das notwendig, damit der nächste Request mit Zeitbereich funktioniert
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
        # DEBUG
        img_file='/tmp/energy_chart_current.png'
        with open(img_file, 'wb') as file:
            file.write(resp.content)
        print("Energy chart written to {}".format(img_file))

    # Chart MIT Zeitparameter
    url = 'https://www.sunnyportal.com/PortalCharts/Core/PortalChartsAPI.aspx'
    params = {
        'id': 'mainChart',
        'xf': int(start.timestamp()),
        'xt': int(end.timestamp()),
        't': int(time.time() * 1000)
    }
    # DEBUG
    print("Start: {}".format(int(start.timestamp())))
    print("End  : {}".format(int(end.timestamp())))
    resp = session.get(url, params=params, headers=headers)
    if not resp.ok:
        return None
    else:
        print("Get Energy Chart OK")
        # DEBUG
        img_file='/tmp/energy_chart_history.png'
        with open(img_file, 'wb') as file:
            file.write(resp.content)
        print("Energy chart written to {}".format(img_file))

    url = 'https://www.sunnyportal.com/PortalCharts/Core/PortalChartsAPI.aspx'
    params = {
        'id': 'mainChart',
        'mode': 'last_info',
        't': int(time.time() * 1000)
    }
    resp = session.get(url, params=params, headers=headers)
    if not resp.ok:
        return None
    else:
        print("Get Last Info OK")

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
    try:
        with open('.config.json', 'r') as config_file:
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
    print_dashboard_info(session, headers)
    get_energy_chart(session, headers, datetime.datetime(2023, 1, 1, 0, 0, tzinfo=cet_tz), datetime.datetime(2023, 1, 2, 0, 0, tzinfo=cet_tz))

if __name__ == "__main__":
    main()
