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
        #"__VIEWSTATE": "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",
        #"__VIEWSTATEGENERATOR": "4E24AF74",
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

    url = 'https://www.sunnyportal.com/FixedPages/HoManEnergyRedesign.aspx/GetLegendWithValues'
    data = {
        # Webseite nimmt hier was leicht anderes. Bedeutung unklar
        #'anchorTime': int(end.timestamp()),
        'anchorTime': 1672531200,
        'tabNumber': 1
    }
    resp = session.post(url, json=data, headers=headers)
    if not resp.ok:
        return None
    else:
        print("Post Legend OK")

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
