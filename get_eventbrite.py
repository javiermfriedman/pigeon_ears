#!/usr/bin/env python3
import os
import requests
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def fetch_all_nyc_music_events(date: datetime):
    token = os.getenv("EVENTBRITE_OAUTH_TOKEN")
    if not token:
        raise RuntimeError(
            "❌ No EVENTBRITE_OAUTH_TOKEN found. "
            "Please set it in your .env file as EVENTBRITE_OAUTH_TOKEN."
        )

    url = "https://www.eventbriteapi.com/v3/events/search/"
    # Format start/end times in UTC (no fractional seconds)
    start_dt = date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    end_dt   = (date + timedelta(days=1)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "location.address": "New York",
        "categories": "103",  # Music category ID
        "start_date.range_start": start_dt,
        "start_date.range_end": end_dt,
        "page": 1
    }

    all_events = []
    while True:
        # Debug: print the full request URL
        prepared = requests.Request("GET", url, headers=headers, params=params).prepare()
        print(f"Requesting page {params['page']}: {prepared.url}")

        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()

        events = data.get("events", [])
        all_events.extend(events)

        pagination = data.get("pagination", {})
        page_num   = pagination.get("page_number", 1)
        page_count = pagination.get("page_count", 1)

        if page_num >= page_count:
            break
        params["page"] = page_num + 1

    return all_events

def main():
    # Fetch events for "today" in UTC
    today = datetime.now(timezone.utc)
    events = fetch_all_nyc_music_events(today)

    print(f"Fetched {len(events)} events total\n")
    # pretty-print the list of events (you can process/parse this further)
    print(json.dumps(events, indent=2))

if __name__ == "__main__":
    main()
