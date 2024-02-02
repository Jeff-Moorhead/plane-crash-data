#!/usr/bin/env python3

import argparse
from datetime import datetime
import json

from scraper import scraper


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start", type=int, default=1920)
    parser.add_argument("-e", "--end", type=int, default=datetime.today().year)

    return parser.parse_args()


def main():
    args = get_args()
    s = scraper.Scraper(start_year=args.start, end_year=args.end)
    s.scrape()
    with open("output.json", "w+", encoding="utf-8") as f:
        json.dump(s.processed_data, f)


if __name__ == "__main__":
    main()
