import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse

# harcoded URL for extraction
BASE_URL = "https://www.skatteverket.se/foretag/skatterochavdrag/avdragforforetag/avdragslexikonforetag.4.3684199413c956649b550c8.html"


def extract_text_from_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    page_text = soup.get_text(strip=True)
    print(page_text)

extract_text_from_html(BASE_URL)