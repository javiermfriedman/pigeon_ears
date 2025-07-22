"""
This script fetches all music events in NYC for a given date from Ticketmaster.
"""

#!/usr/bin/env python3
import os
import requests
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

def fetch_all_nyc_music_events(date: datetime):
    api_key = os.getenv('TICKETMASTER_API_KEY')
    if not api_key:
        raise RuntimeError("❌ No TICKETMASTER_API_KEY found in environment")

    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    start_dt = date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    end_dt   = (date + timedelta(days=1)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    all_events = []
    page = 0
    size = 200  # max per Ticketmaster docs

    while True:
        params = {
            "apikey": api_key,
            "classificationName": "music",
            "city": "New York",
            "countryCode": "US",
            "startDateTime": start_dt,
            "endDateTime": end_dt,
            "size": size,
            "page": page
        }

        # Debug
        prepared = requests.Request("GET", url, params=params).prepare()
        print(f"Requesting page {page}: {prepared.url}")

        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        # Extract and accumulate
        events = data.get("_embedded", {}).get("events", [])
        all_events.extend(events)

        # Pagination info
        page_info = data.get("page", {})
        total_pages = page_info.get("totalPages", 0)
        if page >= total_pages - 1:
            break

        page += 1

    return all_events

def main():
    today = datetime.now(timezone.utc)
    events = fetch_all_nyc_music_events(today)
    print(f"Fetched {len(events)} events total\n")
    print(json.dumps(events, indent=2))  # or process however you like

if __name__ == "__main__":
    main()
