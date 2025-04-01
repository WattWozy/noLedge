import requests
from bs4 import BeautifulSoup
import time
import os
from urllib.parse import urljoin, urlparse
from text_sucker import extract_and_save_text

# Base URL and subdomain
BASE_URL = "https://sede.agenciatributaria.gob.es/"
SUBDOMAIN = "sede.agenciatributaria.gob.es"

# Set to keep track of visited URLs
visited = set()

def sanitize_filename(url):
    """Generate a safe filename from the URL path."""
    parsed_url = urlparse(url)
    filename = parsed_url.path.strip('/').replace('/', '_')
    return filename if filename else "index"

def crawl(url, output_dir):
    """
    Crawl the website starting from the given URL
    """
    if url in visited:
        return
        
    visited.add(url)
    print(f"Crawling: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Determine output file path
        filename = sanitize_filename(url) + ".txt"
        output_file = os.path.join(output_dir, filename)
        
        # Extract and save text from this page
        extract_and_save_text(url, response.text, output_file)
        
        # Extract links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            full_link = urljoin(url, href)
            if urlparse(full_link).netloc == SUBDOMAIN:
                crawl(full_link, output_dir)
            else:
                print(f"Skipping external link: {full_link}")
    
    except requests.RequestException as e:
        print(f"Failed to crawl {url}: {e}")
    
    time.sleep(2)

def main():
    output_dir = "scraped_texts"
    os.makedirs(output_dir, exist_ok=True)
    
    crawl(BASE_URL, output_dir)
    
    print(f"\nCrawling complete. Visited {len(visited)} pages.")
    print(f"Content saved in {output_dir}/")

if __name__ == "__main__":
    main()
