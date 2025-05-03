import requests
from bs4 import BeautifulSoup
import logging
import json
import sys
import io
import time # Added for potential delays

# Configure logging (same as before)
# logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
# Keep INFO level for cleaner output unless debugging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# --- Helper function (optional but useful) ---
def get_soup(url, headers):
    """Fetches URL and returns BeautifulSoup object or None on error."""
    try:
        logger.info(f"Sending request to: {url}")
        response = requests.get(url, headers=headers, timeout=15) # Added timeout
        response.raise_for_status()
        logger.info(f"Response status code: {response.status_code} from {url}")
        # Use lxml for potentially better parsing speed and handling broken HTML
        soup = BeautifulSoup(response.content, 'lxml') # Changed parser, ensure lxml is installed: pip install lxml
        # If lxml causes issues, fallback: soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except requests.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error parsing {url}: {e}", exc_info=True)
        return None

# --- NEW FUNCTION ---
def scrape_article_text(article_url: str) -> str | None:
    """
    Scrapes the raw text content from a single news article page.

    Args:
        article_url: The URL of the news article to scrape.

    Returns:
        A string containing the extracted raw text, or None if extraction fails.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    soup = get_soup(article_url, headers)
    if not soup:
        return None # Error handled in get_soup

    # --- Find the main content area (NEEDS ADJUSTMENT PER SITE) ---
    # This is the most critical part and requires inspecting the target site's HTML.
    # Try common patterns. Add more selectors specific to the sites you target.
    content_area = None
    possible_selectors = [
        {'name': 'div', 'attrs': {'class': 'article-content'}}, # Common class
        {'name': 'div', 'attrs': {'class': 'story-body'}},     # Another common class
        {'name': 'div', 'attrs': {'class': 'article-body'}},   # Yet another
        {'name': 'div', 'attrs': {'id': 'main-content'}},     # Common ID
        {'name': 'article'},                                 # Semantic HTML5 tag
        # Add more site-specific selectors here if needed
        # e.g., {'name': 'main', 'attrs': {'role': 'main'}}
    ]

    for selector in possible_selectors:
        logger.debug(f"Trying selector: {selector}")
        content_area = soup.find(selector['name'], selector.get('attrs', {}))
        if content_area:
            logger.info(f"Found content area using selector: {selector}")
            break # Stop searching once found

    if not content_area:
        logger.warning(f"Could not find a specific main content container for {article_url}. "
                       "Falling back to finding all <p> tags in the <body>.")
        # If no specific container found, use the whole body as fallback context
        content_area = soup.body
        if not content_area:
            logger.error(f"Could not even find the <body> tag for {article_url}. Aborting text extraction.")
            return None


    # --- Extract text from paragraph tags within the content area ---
    paragraphs = content_area.find_all('p')
    logger.info(f"Found {len(paragraphs)} paragraph tags within the selected area.")

    # Filter out paragraphs that might be captions, ads, or metadata
    # This is heuristic - adjust keywords as needed
    ignore_keywords = ['copyright', 'foto:', 'photo:', 'izvor:', 'source:', 'piše:', 'autor:', 'objavljeno:', 'updated:']
    ignore_classes = ['caption', 'credit', 'related-links', 'ad-wrapper'] # Add classes to ignore

    article_paragraphs = []
    for p in paragraphs:
        # Check if the paragraph or its parent has an ignored class
        has_ignored_class = False
        for cls in ignore_classes:
            if p.find_parent(class_=cls) or cls in p.get('class', []):
                has_ignored_class = True
                break
        if has_ignored_class:
            logger.debug(f"Ignoring paragraph due to class: {p.get_text(strip=True)[:50]}...")
            continue

        # Get text and check for ignored keywords
        text = p.get_text(strip=True)
        if text:
            lower_text_start = text.lower()[:30] # Check start of text
            if any(keyword in lower_text_start for keyword in ignore_keywords):
                logger.debug(f"Ignoring paragraph due to keyword: {text[:50]}...")
                continue
            # Check if it mostly contains links (common in related articles sections)
            links_in_p = p.find_all('a')
            link_text_len = sum(len(link.get_text(strip=True)) for link in links_in_p)
            if len(links_in_p) > 0 and link_text_len > len(text) * 0.7: # If >70% of text is link text
                logger.debug(f"Ignoring paragraph likely containing only links: {text[:50]}...")
                continue

            article_paragraphs.append(text)

    if not article_paragraphs:
        logger.warning(f"Could not extract any valid paragraph text from {article_url}")
        # As a last resort, try getting all text from the identified content_area directly
        # This might include unwanted navigation/metadata text mixed in.
        if content_area != soup.body: # Only if we found a specific area
            fallback_text = content_area.get_text(separator='\n', strip=True)
            if fallback_text:
                logger.warning("Returning ALL text from the identified content area as fallback.")
                return fallback_text
        return None # Give up if no paragraphs found

    # --- Combine and return the text ---
    full_text = "\n\n".join(article_paragraphs) # Join paragraphs with double newlines
    logger.info(f"Successfully extracted approx. {len(full_text)} characters of text from {article_url}")
    return full_text


# --- Your Existing Functions (Slightly modified logger level) ---

def debug_html_structure(soup):
    """Debug function to understand the HTML structure"""
    logger.debug("HTML Structure Analysis:")
    logger.debug(f"Total article elements found: {len(soup.find_all('article'))}")
    first_article = soup.find('article')
    if first_article:
        logger.debug("First article HTML:")
        logger.debug(first_article.prettify()[:500] + "...")
    else:
        logger.debug("No article elements found")
    all_h3 = soup.find_all('h3')
    logger.debug(f"Total h3 elements found: {len(all_h3)}")
    for i, h3 in enumerate(all_h3[:3]):
        logger.debug(f"h3[{i}] classes: {h3.get('class', [])} | Text: {h3.text.strip()[:50]}")


def scrape_021_rs_index(): # Renamed slightly for clarity
    """
    Scrape article titles and links from the 021.rs index page.
    """
    url = "https://www.021.rs/Najnovije/3"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    soup = get_soup(url, headers)
    if not soup:
        return [] # Error handled in get_soup

    # Debug the HTML structure (only if needed)
    # debug_html_structure(soup)

    # Find all article elements (adjust selector if needed for 021.rs index)
    # Inspecting 021.rs/Najnovije/3, articles seem to be in <div class="articleTeaser">
    articles = soup.find_all('div', class_='articleTeaser') # Adjusted selector based on inspection
    if not articles:
        logger.warning("No 'div' with class 'articleTeaser' found. Trying original 'article' tag.")
        articles = soup.find_all('article') # Fallback to original attempt

    logger.info(f"Found {len(articles)} potential article entries on index page.")

    article_data = []
    base_url = "https://www.021.rs" # Needed to construct full URLs

    for idx, article_container in enumerate(articles):
        # Find the link and title within the container
        # Based on inspection, the link/title is in <h3 class="articleTitle"><a><span>...</span></a></h3>
        title_element = article_container.find('h3', class_='articleTitle')
        if not title_element:
            logger.warning(f"Skipping entry {idx+1}: No 'h3' with class 'articleTitle' found.")
            # logger.debug(f"Entry {idx + 1} HTML:\n{article_container.prettify()[:200]}")
            continue

        link_element = title_element.find('a')
        if not link_element:
            logger.warning(f"Skipping entry {idx+1}: No 'a' tag found within the 'h3'.")
            continue

        relative_link = link_element.get('href')
        title_span = link_element.find('span')
        title = title_span.text.strip() if title_span else link_element.text.strip() # Get title from span or <a>

        if title and relative_link:
            # Construct absolute URL
            if relative_link.startswith('/'):
                full_link = base_url + relative_link
            else:
                full_link = relative_link # Assuming it might already be absolute

            # Exclude ad links (example, adjust if needed)
            if "/oglasi" not in full_link:
                article_data.append({
                    'title': title,
                    'link': full_link # Store the full link
                })
                logger.info(f"Extracted index entry {idx + 1}: {title[:60]}...")
            else:
                logger.info(f"Skipping ad link: {full_link}")
        else:
            logger.warning(f"Skipping entry {idx+1}: Missing title or link.")

    logger.info(f"Successfully extracted {len(article_data)} article links from index.")
    return article_data


# --- Main Execution Logic ---
if __name__ == "__main__":
    # Set UTF-8 output
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    logger.info("--- Step 1: Scraping article list from 021.rs index ---")
    articles_list = scrape_021_rs_index()

    if not articles_list:
        logger.warning("No articles found on the index page. Exiting.")
        sys.exit(1) # Exit if index scraping failed

    logger.info(f"\n--- Step 2: Scraping text content for {len(articles_list)} articles ---")

    all_scraped_data = []
    for i, article_info in enumerate(articles_list):
        logger.info(f"Processing article {i+1}/{len(articles_list)}: {article_info['title']}")
        article_text = scrape_article_text(article_info['link'])

        if article_text:
            all_scraped_data.append({
                'title': article_info['title'],
                'link': article_info['link'],
                'text': article_text # Add the scraped text
            })
            # Optionally print progress or summary here
            # print(f"--- Article: {article_info['title']} ---")
            # print(article_text[:200] + "...\n") # Print snippet
        else:
            logger.warning(f"Failed to extract text for: {article_info['title']} ({article_info['link']})")
            # Optionally store failed ones too
            all_scraped_data.append({
                'title': article_info['title'],
                'link': article_info['link'],
                'text': None # Indicate failure
            })


        # --- BE POLITE: Add a delay between requests ---
        delay_seconds = 1 # Adjust as needed (1-3 seconds is usually reasonable)
        logger.info(f"Waiting for {delay_seconds} second(s)...")
        time.sleep(delay_seconds)


    logger.info("\n--- Step 3: Outputting Results ---")
    # Example: Print the first article's full data as JSON
    if all_scraped_data:
        print("\n--- Example Output (First Article JSON) ---")
        print(json.dumps(all_scraped_data[0], indent=2, ensure_ascii=False)) # Pretty print JSON

        # Example: Save all data to a JSON file
        output_filename = "scraped_articles_with_text.json"
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(all_scraped_data, f, indent=2, ensure_ascii=False)
            logger.info(f"All scraped data saved to {output_filename}")
        except IOError as e:
            logger.error(f"Failed to write output file: {e}")

    else:
        logger.warning("No text could be scraped from any articles.")


    logger.info("\n--- Scraping process completed! ---")