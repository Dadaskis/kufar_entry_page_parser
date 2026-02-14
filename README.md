# Kufar.by Scraper

A Python script to scrape ads from the entry page of Kufar.by, extracting listings including titles, prices, regions, phone numbers (WIP), and detailed descriptions.

## Features

- Scrapes all listings from the main page
- Extracts title, price, region, and item ID for each listing
- Fetches phone numbers via Kufar's API
- Retrieves detailed descriptions and parameters from individual item pages
- Handles timeouts and errors... kinda

## Requirements

- Python 3.6+
- requests
- beautifulsoup4

## Installation

Clone this repository:
```bash
git clone https://github.com/Dadaskis/kufar_entry_page_parser
cd kufar-scraper
```