"""
Test end-to-end scraper
"""
from .scraper import Scraper


def test_scraper():
    s = Scraper(start_year=1970, end_year=1970)
    want_headers = {
        0: "date",
        1: "location",
        2: "operator",
        3: "aircraft type",
        4: "registration",
        5: "fatalities",
    }
    want_data = [
            "05 jan 1970",
            "stockholm, sweden",
            "spantax",
            "convair cv-990-30a-5",
            "ec-bnm",
            "5/10(0)",
        ]

    s.scrape()

    assert s.processed_data["headers"] == want_headers
    assert s.processed_data["data"][0] == want_data
