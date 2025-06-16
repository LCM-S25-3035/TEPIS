#!/usr/bin/env python
# coding: utf-8

import requests
import pandas as pd
import os

# Ticketmaster API KEY
API_KEY = 'LEIeBeElcqIf6xxGthrDmG1t5Ga7Weyq'
url = 'https://app.ticketmaster.com/discovery/v2/events.json'

# Cities to search (10 in Canada, 10 in USA)
cities = [
    ['Toronto', 'CA'],
    ['Montreal', 'CA'],
    ['Vancouver', 'CA'],
    ['Calgary', 'CA'],
    ['Ottawa', 'CA'],
    ['Edmonton', 'CA'],
    ['Winnipeg', 'CA'],
    ['Quebec City', 'CA'],
    ['Hamilton', 'CA'],
    ['Kitchener', 'CA'],
    ['New York', 'US'],
    ['Los Angeles', 'US'],
    ['Chicago', 'US'],
    ['Houston', 'US'],
    ['Phoenix', 'US'],
    ['Philadelphia', 'US'],
    ['San Antonio', 'US'],
    ['San Diego', 'US'],
    ['Dallas', 'US'],
    ['San Jose', 'US']
]

all_events = []

# Collect data for all cities
for city, country in cities:
    parameters = {
        'apikey': API_KEY,
        'city': city,
        'countryCode': country,
        'size': 100
    }

    try:
        response = requests.get(url, params=parameters)
        data = response.json()

        if '_embedded' in data:
            for event in data['_embedded']['events']:
                venue = event['_embedded']['venues'][0]
                price_info = event.get('priceRanges', [{}])[0]
                image_url = event['images'][0]['url'] if event.get('images') else None

                event_data = {
                    "event_title": event.get('name'),
                    "summary": event.get('info', ''),
                    "image_url": image_url,
                    "language": '',
                    "event_type": event.get('classifications', [{}])[0].get('segment', {}).get('name', ''),
                    "event_host": event.get('promoter', {}).get('name', ''),
                    "ticket_price": price_info.get('min'),
                    "booking_url": event.get('url'),
                    "start_date": event.get('dates', {}).get('start', {}).get('localDate'),
                    "end_date": '',
                    "start_time": event.get('dates', {}).get('start', {}).get('localTime'),
                    "end_time": '',
                    "event_place": venue.get('name'),
                    "full_address": venue.get('address', {}).get('line1', ''),
                    "country_name": venue.get('country', {}).get('name', ''),
                    "state_name": venue.get('state', {}).get('name', ''),
                    "city_name": venue.get('city', {}).get('name', ''),
                    "postal_code": venue.get('postalCode', '')
                }

                all_events.append(event_data)

    except Exception as e:
        print(f"Error loading events for {city}, {country}: {e}")

# Save events to CSV with deduplication
csv_path = "ticketmaster_events.csv"
df = pd.DataFrame(all_events)

print(f"Total new events scraped: {len(all_events)}")

if os.path.exists(csv_path):
    print("Merging with existing CSV...")
    df_existing = pd.read_csv(csv_path)
    df = pd.concat([df_existing, df], ignore_index=True)
    print(f"Before removing duplicates: {len(df)} rows")
    df.drop_duplicates(subset=["event_title", "start_date", "city_name"], inplace=True)
    print(f"After removing duplicates: {len(df)} rows")

df.to_csv(csv_path, index=False)
print("CSV updated successfully.")

# Download images
image_folder = "C:/Users/yorbi/OneDrive - Lambton College/Term 3/Capstone/Project/Event_Images"
os.makedirs(image_folder, exist_ok=True)

for index, row in df.iterrows():
    image_url = row["image_url"]
    event_title = row["event_title"]

    if pd.notna(image_url):
        try:
            safe_title = "".join(c for c in event_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title[:40].replace(' ', '_')}_{index}.jpg"
            image_path = os.path.join(image_folder, filename)

            img_data = requests.get(image_url).content
            with open(image_path, 'wb') as handler:
                handler.write(img_data)

        except Exception as e:
            print(f"Downloading image error for {event_title}: {e}")
