import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://in.bookmyshow.com/explore/events-{}"

def fetch_events(city):
    url = BASE_URL.format(city.lower())
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    events = []
    cards = soup.select("div[class*='style__StyledEventCard']")

    for card in cards:
        name = card.select_one("h3")
        link = card.find("a")
        meta = card.select_one("div[class*='style__EventMeta']")

        if not name or not link or not meta:
            continue

        events.append({
            "event_name": name.text.strip(),
            "date": meta.text.strip(),
            "venue": city,
            "city": city,
            "category": "Event",
            "url": "https://in.bookmyshow.com" + link["href"],
            "status": "Upcoming",
            "last_updated": datetime.now().strftime("%Y-%m-%d")
        })

    return events
city = input("Enter city (eg: Jaipur, Delhi, Mumbai): ")
events = fetch_events(city)
#google sheets
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

def update_sheet(events):
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope)

    client = gspread.authorize(creds)
    sheet = client.open("Pixie_Event_Tracker").sheet1

    existing = pd.DataFrame(sheet.get_all_records())

    for event in events:
        if not existing.empty and event["url"] in existing["url"].values:
            idx = existing[existing["url"] == event["url"]].index[0] + 2
            sheet.update(f"A{idx}:H{idx}", [list(event.values())])
        else:
            sheet.append_row(list(event.values()))



