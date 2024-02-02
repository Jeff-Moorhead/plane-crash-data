"""
Implements a scraper that pulls plane crash data from planecrashinfo.com.
Data available from 1920 - 2024.
"""
from datetime import datetime
import logging
import sys
from typing import List

import bs4
import requests

HEADERS = {
    0: "date",
    1: "location",
    2: "operator",
    3: "aircraft type",
    4: "registration",
    5: "fatalities"
}

BASE_URL = "https://planecrashinfo.com"
START_YEAR = 1920

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class DataNotProcessedError(Exception):
    pass


class Scraper():
    def __init__(self, start_year=START_YEAR, end_year=datetime.today().year):
        self.start_year = start_year
        self.end_year = end_year
        self._processed_data = {"headers": {}, "data": []}
    
    @property
    def processed_data(self):
        if len(self._processed_data["headers"]) == 0 or len(self._processed_data["data"]) == 0:
            raise DataNotProcessedError

        return self._processed_data

    def scrape(self):
        content = self._get_content(f"{BASE_URL}/database.htm")
        hrefs = self._get_hrefs_for_years(content)
        content_by_year = []

        for href in hrefs:
            # logging.info(f"processing {href}")
            if not href.startswith("/"):
                href = "/" + href  # some hrefs don't have a leading slash, so we need to add it
            crash_content = self._get_content(f"{BASE_URL}{href}")
            content_by_year.append(self._extract_raw_crash_data(crash_content))

        for row in content_by_year:
            self._process_crash_data(row)

    def _get_content(self, url: str):
        res = requests.get(url, timeout=5)
        res.raise_for_status()

        return res.content

    def _get_hrefs_for_years(self, content: bytes) -> List:
        soup = bs4.BeautifulSoup(content, "html.parser")

        hrefs = []
        for link in soup.find_all("a"):
            href = link["href"]
            if href == "index.html":
                continue
 
            href_year = int(link.text)

            # Don't assume the years will be in order
            if href_year < self.start_year or href_year > self.end_year:
                continue

            hrefs.append(href)

        return hrefs

    def _extract_raw_crash_data(self, content: bytes) -> List[bs4.element.Tag]:
        processed = []
        tags = bs4.BeautifulSoup(content, "html.parser").find_all("td")
        
        for tag in tags:
            processed.append(tag)

        return processed

    def _process_crash_data(self, rows: List[bs4.element.Tag]):
        headers = rows[:4]
        idx = 0
        for element in headers:
            if self._verify_headers(self._processed_data["headers"]):
                break
            fields = map(str.strip, element.text.split("/"))
            for field in fields:
                self._processed_data["headers"][idx] = field.lower()
                idx += 1

        data = rows[4:]
        i = 0
        while i < len(data) - 3:
            group = data[i:i+4]
            row = []

            for elem in group:
                fields = map(str.strip, elem.get_text(separator="<br>").split("<br>"))
                for field in fields:
                    row.append(field.lower())
            
            self._processed_data["data"].append(row)
            i += 4

    def _verify_headers(self, headers: List[str]) -> bool:
        want_headers = HEADERS
        for want in want_headers:
            if want not in headers:
                return False

        return True
