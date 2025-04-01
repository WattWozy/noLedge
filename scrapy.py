import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
from text_sucker import extract_and_save_text

# Base URL and subdomain
BASE_URL = "https://www.niklaswozniak.dev/"
SUBDOMAIN = "www.niklaswozniak.dev"

# Set to keep track of visited URLs
visited = set()

def crawl(url, output_file):
    """
    Crawl the website starting from the given URL
    """
    # Check if the URL has already been visited
    if url in visited:
        return
        
    # Add the URL to the visited set
    visited.add(url)
    print(f"Crawling: {url}")
    
    try:
        # Fetch the page
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract and save text from this page
        extract_and_save_text(url, response.text, output_file)
        
        # Extract links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            # Convert relative links to absolute
            full_link = urljoin(url, href)
            
            # Filter to only include links under the same subdomain
            if urlparse(full_link).netloc == SUBDOMAIN:
                crawl(full_link, output_file)
            else:
                print(f"Skipping external link: {full_link}")
    
    except requests.RequestException as e:
        print(f"Failed to crawl {url}: {e}")
    
    # Delay to be respectful to the server
    time.sleep(2)

def main():
    output_file = "sucked.txt"
    
    # Create or clear the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"TEXT CONTENT FROM {SUBDOMAIN}\n\n")
    
    # Start crawling from the base page
    crawl(BASE_URL, output_file)
    
    # Print summary
    print(f"\nCrawling complete. Visited {len(visited)} pages.")
    print(f"Content saved to {output_file}")

if __name__ == "__main__":
    main()