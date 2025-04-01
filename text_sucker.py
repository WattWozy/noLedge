from bs4 import BeautifulSoup

def extract_text_from_html(html_content):
    """
    Extract clean text content from HTML
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script_or_style in soup(['script', 'style', 'header', 'footer', 'nav']):
        script_or_style.extract()
        
    # Get text
    text = soup.get_text(separator='\n', strip=True)
    
    # Remove excessive newlines and whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

def extract_and_save_text(url, html_content, output_file):
    """
    Extract text from HTML and save it to the output file
    """
    try:
        # Extract text
        text = extract_text_from_html(html_content)
        
        # Save to file
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{'=' * 80}\n")
            f.write(f"SOURCE: {url}\n")
            f.write(f"{'=' * 80}\n\n")
            f.write(text)
            f.write("\n")
            
        print(f"Text extracted and saved from: {url}")
        return True
    except Exception as e:
        print(f"Error extracting text from {url}: {e}")
        return False

# This allows the file to be imported or run directly
if __name__ == "__main__":
    # Example standalone usage
    import requests
    
    url = "https://www.niklaswozniak.dev"
    output_file = "single_page_content.txt"
    
    try:
        response = requests.get(url)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"TEXT CONTENT FROM {url}\n\n")
        
        extract_and_save_text(url, response.text, output_file)
        print(f"Content saved to {output_file}")
    except Exception as e:
        print(f"Error: {e}")