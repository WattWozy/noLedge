import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse

# Base URL and subdomain
BASE_URL = "https://www.skatteverket.se/"
SUBDOMAIN = "www.skatteverket.se"
visited = set()  # Set to keep track of visited URLs


def crawl(url):
   # Check if the URL has already been visited
   if url in visited:
       return

   # Add the URL to the visited set
   visited.add(url)
   print(f"Crawling: {url}")

   try:
       # Fetch the page
       response = requests.get(url)
       response.raise_for_status()  # Raise an error for bad responses
       soup = BeautifulSoup(response.text, 'html.parser')

       # Extract links
       links = soup.find_all('a', href=True)
       for link in links:
           href = link['href']
           # Convert relative links to absolute
           full_link = urljoin(url, href)

           # Filter to only include links under the same subdomain
           if urlparse(full_link).netloc == SUBDOMAIN:
               crawl(full_link)
           else:
               print(f"Skipping external link: {full_link}")

   except requests.RequestException as e:
       print(f"Failed to crawl {url}: {e}")

   # Delay for 2 seconds
   time.sleep(2)

# Start crawling from the main page
crawl(BASE_URL)

# Print the collection of visited URLs
print("Collected URLs:")
for url in visited:
   print(url)


