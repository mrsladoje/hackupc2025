import requests
from bs4 import BeautifulSoup
import logging
import json
import sys
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s') # Changed default level to INFO
logger = logging.getLogger(__name__)

# --- Set log level via command line argument ---
# Example: python your_script.py DEBUG
if len(sys.argv) > 1 and sys.argv[1].upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
    log_level_name = sys.argv[1].upper()
    logging.getLogger().setLevel(getattr(logging, log_level_name))
    logger.info(f"Log level set to: {log_level_name}")
# -----------------------------------------------

def debug_html_structure(soup):
    """Debug function to understand the HTML structure"""
    logger.debug("--- HTML Structure Analysis ---")
    logger.debug(f"Page Title: {soup.title.string if soup.title else 'N/A'}")
    logger.debug(f"Total article elements found: {len(soup.find_all('article'))}")

    # Log first article structure
    first_article = soup.find('article')
    if first_article:
        logger.debug("First article HTML snippet:")
        logger.debug(first_article.prettify()[:500] + "...")
    else:
        logger.debug("No article elements found")

    # Log all h2 elements with class 'news-item-title' (new target)
    all_h2_titles = soup.find_all('h2', class_='news-item-title')
    logger.debug(f"Total h2.news-item-title elements found: {len(all_h2_titles)}")
    for i, h2 in enumerate(all_h2_titles[:3]):  # Log first 3 relevant h2 elements
        logger.debug(f"h2.news-item-title[{i}] | Text: {h2.text.strip()[:60]}")
        link_in_h2 = h2.find('a')
        if link_in_h2:
            logger.debug(f"  -> Link href: {link_in_h2.get('href')}")
        else:
            logger.debug("  -> No <a> tag found inside this h2")

    # Keep logging h3 for comparison/other uses if needed
    all_h3 = soup.find_all('h3')
    logger.debug(f"Total h3 elements found: {len(all_h3)}")
    for i, h3 in enumerate(all_h3[:3]):  # Log first 3 h3 elements
        logger.debug(f"h3[{i}] classes: {h3.get('class', [])} | Text: {h3.text.strip()[:50]}")
    logger.debug("--- End HTML Structure Analysis ---")


def scrape_informer_rs():
    """
    Scrape article titles and links from informer.rs/najnovije-vesti
    """
    base_url = "https://informer.rs"
    target_url = f"{base_url}/najnovije-vesti?page=13"

    # Set up headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }

    try:
        logger.info(f"Sending request to: {target_url}")
        # Send GET request
        response = requests.get(target_url, headers=headers, timeout=15) # Added timeout
        response.raise_for_status()  # Raise an exception for bad status codes

        # Ensure correct encoding
        response.encoding = response.apparent_encoding
        html_content = response.text

        logger.info(f"Response status code: {response.status_code}")
        logger.debug(f"Response content length: {len(html_content)}")

        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Debug the HTML structure (only if log level is DEBUG)
        if logger.isEnabledFor(logging.DEBUG):
            debug_html_structure(soup)

        # Find all article elements
        articles = soup.find_all('article', class_='news-item') # Be more specific if possible
        logger.info(f"Found {len(articles)} potential article elements with class 'news-item'")

        # List to store extracted data
        article_data = []

        # Extract title and link from each article
        for idx, article in enumerate(articles):
            logger.debug(f"\nProcessing article {idx + 1}")

            # Find the H2 element containing the title
            # Corresponds to <h2 class="news-item-title"> in the example
            title_h2_element = article.find('h2', class_='news-item-title')
            logger.debug(f"H2.news-item-title element found: {title_h2_element is not None}")

            if title_h2_element:
                # The link and title text are inside the <a> tag within the H2
                link_element = title_h2_element.find('a')
                logger.debug(f"Link element <a> found inside H2: {link_element is not None}")

                if link_element:
                    # Extract the title text
                    title = link_element.text.strip()
                    logger.debug(f"Title extracted: {title}")

                    # Extract the relative link (href attribute)
                    relative_link = link_element.get('href')
                    logger.debug(f"Relative link extracted: {relative_link}")

                    if relative_link:
                        # Filter out advertisement links or other unwanted patterns
                        if not relative_link.startswith("/oglasi"):
                            # Construct the full absolute link
                            # Ensure no double slashes if relative_link already starts with /
                            full_link = f"{base_url}{relative_link}"
                            logger.debug(f"Full link constructed: {full_link}")

                            article_data.append({
                                'title': title,
                                'link': full_link
                            })
                            logger.debug(f"Successfully extracted article {idx + 1}: '{title[:50]}...'")
                        else:
                            logger.debug(f"Skipping advertisement article {idx + 1} based on link: {relative_link}")
                    else:
                        logger.warning(f"No href attribute found in link element for article {idx + 1}")
                else:
                    logger.warning(f"No link element <a> found inside H2 for article {idx + 1}")
            else:
                # Sometimes titles might be in H3 for different layouts, add a fallback check if needed
                # Example fallback (adjust class/structure if necessary):
                # title_h3_element = article.find('h3', class_='some-other-title-class')
                # if title_h3_element: ... etc ...
                # else:
                logger.warning(f"No H2 element with class 'news-item-title' found in article {idx + 1}")
                # Log the article's HTML for debugging if title element is missing
                logger.debug(f"Article {idx + 1} HTML (if title missing):\n{article.prettify()[:300]}...")


        logger.info(f"Successfully extracted {len(article_data)} articles")
        return article_data

    except requests.Timeout:
        logger.error(f"Request timed out while trying to fetch {target_url}")
        return []
    except requests.RequestException as e:
        logger.error(f"Error fetching the page {target_url}: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred during parsing: {e}", exc_info=True) # Log traceback
        return []

def display_results(data):
    """
    Output articles as JSON, one object per line.
    """
    if not data:
        logger.warning("No articles found to display.")
        print("[]") # Output empty JSON array if nothing found
        return

    # Option 1: Print each article JSON object on a new line
    for article in data:
         try:
             print(json.dumps(article, ensure_ascii=False)) # ensure_ascii=False for non-latin chars
         except Exception as e:
             logger.error(f"Error JSON dumping article: {article}. Error: {e}")

    # Option 2: Print a single JSON array containing all articles (might be harder for Java line-by-line)
    # print(json.dumps(data, indent=2, ensure_ascii=False))


# Main execution
if __name__ == "__main__":
    # Ensure stdout uses UTF-8 encoding, crucial for Serbian characters
    if sys.stdout.encoding != 'utf-8':
         sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    logger.info("Starting web scraper for informer.rs...")
    articles = scrape_informer_rs()

    # Display results
    display_results(articles)

    logger.info(f"Scraping completed! Found {len(articles)} articles.")