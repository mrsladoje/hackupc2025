import requests
from bs4 import BeautifulSoup
import logging
import json
import sys
import io

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def debug_html_structure(soup):
    """Debug function to understand the HTML structure"""
    logger.debug("HTML Structure Analysis:")
    logger.debug(f"Total article elements found: {len(soup.find_all('article'))}")
    
    # Log first article structure
    first_article = soup.find('article')
    if first_article:
        logger.debug("First article HTML:")
        logger.debug(first_article.prettify()[:500] + "...")
    else:
        logger.debug("No article elements found")
    
    # Log all h3 elements with their classes
    all_h3 = soup.find_all('h3')
    logger.debug(f"Total h3 elements found: {len(all_h3)}")
    for i, h3 in enumerate(all_h3[:3]):  # Log first 3 h3 elements
        logger.debug(f"h3[{i}] classes: {h3.get('class', [])} | Text: {h3.text.strip()[:50]}")

def scrape_021_rs():
    """
    Scrape article titles and links from 021.rs
    """
    url = "https://www.021.rs/Najnovije/3"
    
    # Set up headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        logger.info(f"Sending request to: {url}")
        # Send GET request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response content length: {len(response.text)}")
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug the HTML structure
        debug_html_structure(soup)
        
        # Find all article elements
        articles = soup.find_all('article')
        logger.info(f"Found {len(articles)} article elements")
        
        # List to store extracted data
        article_data = []
        
        # Extract title and link from each article
        for idx, article in enumerate(articles):
            logger.debug(f"\nProcessing article {idx + 1}")
            
            # Find the title element
            title_element = article.find('h3', class_='articleTitle')
            logger.debug(f"Title element found: {title_element is not None}")
            
            if title_element:
                # Try to find span directly
                span_element = title_element.find('span')
                logger.debug(f"Span element found: {span_element is not None}")
                
                if span_element:
                    title = span_element.text.strip()
                    logger.debug(f"Title extracted: {title}")
                else:
                    # If no span, try to get text directly from h3
                    title = title_element.text.strip()
                    logger.debug(f"Title from h3 directly: {title}")
                
                # Extract the link
                link_element = title_element.find('a')
                logger.debug(f"Link element found: {link_element is not None}")
                
                if link_element:
                    link = link_element.get('href')
                    logger.debug(f"Link extracted: {link}")
                    

                    if not link.startswith("/oglasi"):
                        article_data.append({
                            'title': title,
                            'link': link
                        })
                    logger.info(f"Successfully extracted article {idx + 1}: {title[:50]}...")
                else:
                    logger.warning(f"No link found in article {idx + 1}")
            else:
                logger.warning(f"No title element found in article {idx + 1}")
                # Log the article's HTML for debugging
                logger.debug(f"Article {idx + 1} HTML:\n{article.prettify()[:200]}")
        
        logger.info(f"Successfully extracted {len(article_data)} articles")
        return article_data
    
    except requests.RequestException as e:
        logger.error(f"Error fetching the page: {e}")
        return []
    except Exception as e:
        logger.error(f"Error parsing the page: {e}", exc_info=True)
        return []

def display_results(data):
    """
    Output articles as JSON for Java to parse
    """
    if not data:
        logger.warning("No articles found to display")
        return
    
    # Output each article as JSON
    for article in data:
        print(json.dumps(article))

# Main execution
if __name__ == "__main__":
    # Set UTF-8 output
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    logger.info("Starting web scraper for 021.rs...")
    articles = scrape_021_rs()
    
    # Display results
    display_results(articles)
    
    logger.info("Scraping completed!")