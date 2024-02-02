import bs4
import pytest
from requests.exceptions import HTTPError

from . import scraper


def get_scraper():
    return scraper.Scraper(1970, 1970)


def test_get_content():
    s = get_scraper()
    url = "https://planecrashinfo.com/database.htm"
    try:
        res = s._get_content(url)
    except HTTPError as e:
        pytest.fail(f"HTTP Error: {e}")

    assert len(res) > 0


def test_get_hrefs_for_years():
    s = get_scraper()
    content = b"<html><body><a href='/1970/1970.htm'>1970</a><a href='index.html'>index</a></body></html>"
    hrefs = s._get_hrefs_for_years(content)

    assert len(hrefs) == 1 and hrefs[0] == "/1970/1970.htm"


def test_get_hrefs_for_years_out_of_bounds_year():
    # s.start_year = 1970 and s.end_year = 1970
    s = get_scraper()
    content = b"<html><body><a href='/1925/1925.htm'>1925</a></body></html>"
    hrefs = s._get_hrefs_for_years(content)

    assert len(hrefs) == 0


def test_extract_raw_crash_data():
    s = get_scraper()
    content = b"""\
        <html>
          <body>
            <td>Date</td>
            <td>Location / Operator</td>
            <td>Aircraft Type / Registration</td>
            <td>Fatalities</td>
            <td>23 Oct 2024</td>
            <td>New Jersey<br>United</td>
            <td>Boeing 737 Max 9<br>N2794B</td>
            <td>100/200(0)</td>
          </body>
        </html>
    """
    data = s._extract_raw_crash_data(content)
    assert data[0].text == "Date"


def test_process_crash_data_raises_exception():
    s = get_scraper()
    with pytest.raises(scraper.DataNotProcessedError):
        _ = s.processed_data


def test_process_crash_data():
    s = get_scraper()
    content = b"""\
        <html>
          <body>
            <td>Date</td>
            <td>Location / Operator</td>
            <td>Aircraft Type / Registration</td>
            <td>Fatalities</td>
            <td>23 Oct 2024</td>
            <td>New Jersey<br>United</td>
            <td>Boeing 737 Max 9<br>N2794B</td>
            <td>100/200(0)</td>
          </body>
        </html>
    """
    soup = bs4.BeautifulSoup(content, "html.parser")
    data = soup.find_all("td")
    s._process_crash_data(data)

    assert s.processed_data["headers"] == {
        0: "date",
        1: "location",
        2: "operator",
        3: "aircraft type",
        4: "registration",
        5: "fatalities"
    }
    assert s.processed_data["data"] == [
        [
            "23 oct 2024",
            "new jersey",
            "united",
            "boeing 737 max 9",
            "n2794b",
            "100/200(0)",
        ],
    ]


def test_verify_headers():
    s = get_scraper()
    complete_headers = {
        0: "date",
        1: "location",
        2: "operator",
        3: "aircraft type",
        4: "registration",
        5: "fatalities"
    }
    incomplete_headers = {0: "date", 1: "location"}

    assert s._verify_headers(complete_headers)
    assert not s._verify_headers(incomplete_headers)
