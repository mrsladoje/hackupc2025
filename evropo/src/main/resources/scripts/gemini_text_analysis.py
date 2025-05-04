import google.generativeai as genai
import os
import json
import argparse
import requests # Added for fetching URL content
from bs4 import BeautifulSoup # Added for HTML parsing

# Configure the Gemini API key
# Make sure to set the GOOGLE_API_KEY environment variable
# or replace os.getenv("GOOGLE_API_KEY") with your actual key.

# --- IMPORTANT SECURITY NOTE ---
# Hardcoding API keys is insecure. Use environment variables in production.
# Replace 'YOUR_GEMINI_API_KEY' with your actual key ONLY for testing,
# or preferably, set the GOOGLE_API_KEY environment variable.
# GOOGLE_API_KEY = 'YOUR_GEMINI_API_KEY' 
# Using environment variable is the recommended approach:
GOOGLE_API_KEY = "AIzaSyCk7UjfnFNUIKH9j5adD4WNNXc90qHpn5E"

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    print("Please set the GOOGLE_API_KEY environment variable before running the script.")
    # You might want to exit here in a real application
    # exit(1)
    # Using a placeholder for demonstration if env var is not set
    print("Warning: Using a placeholder API key 'halal'. This will likely fail.")
    GOOGLE_API_KEY = 'halal' # Placeholder - replace or set env var


try:
    genai.configure(api_key=GOOGLE_API_KEY)
except TypeError as e:
    # This specific error check might not be necessary if we check GOOGLE_API_KEY first
    print(f"Error configuring Gemini API: {e}")
    print("Ensure the GOOGLE_API_KEY is set correctly.")
    exit(1)
except Exception as e:
    print(f"An unexpected error occurred during Gemini configuration: {e}")
    exit(1)


# Initialize the Gemini model
try:
    # Using a specific, robust model. Check availability if needed.
    model = genai.GenerativeModel('gemini-1.5-flash') # Updated model, check if 'gemini-2.5-flash-preview-04-17' is still desired/available
except Exception as e:
    print(f"Error initializing Gemini model: {e}")
    exit(1)

def scrape_article_text(url, source_type):
    """
    Scrapes the main article text from a given URL based on the source type.

    Args:
        url (str): The URL of the article page.
        source_type (str): The source identifier ('021.rs' or 'informer.rs').

    Returns:
        str: The extracted article text, or None if scraping fails.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        article_div = None

        if source_type == '021.rs':
            # Target the specific div containing the main story content
            article_div = soup.find('div', class_='story')
            if not article_div:
                 # Fallback or more specific selector if the main one fails
                 # Sometimes the core text is within storyBody
                 article_div = soup.find('div', class_='storyBody')

        elif source_type == 'informer.rs':
            # Target the div containing the news content
            article_div = soup.find('div', class_='single-news')
            if not article_div:
                 # Fallback or more specific selector
                 article_div = soup.find('div', class_='single-news-content') # Often text is here

        else:
            print(f"Error: Unsupported source type '{source_type}'.")
            return None

        if article_div:
            # Extract text, joining paragraphs/elements with a space
            # Remove script/style tags first to avoid including their content
            for script_or_style in article_div(['script', 'style']):
                script_or_style.decompose()

            # Get text, ensuring separation between elements and stripping extra whitespace
            text_content = article_div.get_text(separator=' ', strip=True)
            
            # Basic check if text was extracted
            if not text_content:
                print(f"Warning: Found the target div for {source_type}, but it contained no text.")
                return None # Or return "" depending on how you want to handle empty divs

            # Optional: Clean up excessive whitespace/newlines if needed
            text_content = ' '.join(text_content.split())
            return text_content
        else:
            print(f"Error: Could not find the specified article container div for source '{source_type}' at URL {url}.")
            print("Please check the class names ('story' for 021.rs, 'single-news' for informer.rs) are still correct on the website.")
            return None

    except Exception as e:
        print(f"An error occurred during parsing or text extraction: {e}")
        return None


def analyze_text_sentiment(text_to_analyze):
    """
    Analyzes the input text using the Gemini API based on the predefined prompt.

    Args:
        text_to_analyze: The string containing the text to analyze (scraped article).

    Returns:
        A dictionary containing the analysis in JSON format,
        or None if an error occurs.
    """
    # --- Using the complex prompt provided in the request ---
    prompt = f"""
You are an advanced text analysis model. Your task is to analyze the following article, potentially about a student protest or other events, and return a structured JSON output containing specific metrics.

Use the structure and detailed explanation below to perform your analysis accurately:

---

### **JSON Output Structure and Field Descriptions**

''' JSON
{{
    "analysis": {{
        "mentions_protest": true | false,
        "protest_info": {{
            "organizer": "If it is organized by the State, govornment or SNS - the leading political party, or "students who want to learn" who are basically govornment paid people, put "gov", if organized by students or citizens, put "s&o", otherwise 'unknown'",
            "date": "Date of the protest (not the article publication date), in YYYY-MM-DD format if possible, otherwise 'unknown'",
            "location": "City or area where the protest is occurring, if mentioned, otherwise 'unknown'. Try to put the city rather than a more specific location, for example if ETF is mentioned, put "Beograd". Also, it must not be a city outside of Serbia,
            "count": {{
                "government": Number | null,
                "independent": Number | null
            }}
        }}
    }},
    "source": "Name of the publication or source (e.g., 021.rs, Informer, N1, BBC), if identifiable from text or context, otherwise 'unknown'",
    "date_of_news_issue": "Date when this article was published, in YYYY-MM-DD format if possible, otherwise 'unknown'",
    "state_driven_messaging": Integer between 0 and 10,
    "pro_student_messaging": Integer between 0 and 10,
    "student_mentions": {{
        "good_count": Number | 0,
        "bad_count": Number | 0
    }},
    "state_mentions": {{
        "good_count": Number | 0,
        "bad_count": Number | 0
    }},
    "propaganda_count": Number,
    "pro_protest_count": Number  
}}
'''

---

### Explanation of Each Metric

#### `analysis.mentions_protest`
* Return `true` if the article directly references a protest, demonstration, blockade, or similar collective action by students or related groups.
* Return `false` if no such event is mentioned.

#### `analysis.protest_info.organizer`
* Name the individual(s), student group, political group, or organization responsible for organizing the protest/action. If not mentioned, use "unknown".

#### `analysis.protest_info.date`
* Extract the actual date(s) of the protest/action as stated in the article, not the date of publication. Use YYYY-MM-DD format if possible. If not mentioned, use "unknown".

#### `analysis.protest_info.location`
* Provide the geographical location (city, faculty, area) where the protest/action took place. If not mentioned, use "unknown".

#### `analysis.protest_info.count.government`
* Extract the **estimated number of people** attending the protest *as reported by government or pro-government sources*.
* Return the number as an integer if found.
* Return `null` if no such estimate from a government source is mentioned in the text.

#### `analysis.protest_info.count.independent`
* Extract the **estimated number of people** attending the protest *as reported by independent sources* (e.g., organizers, independent media, observers).
* Return the number as an integer if found.
* Return `null` if no such estimate from an independent source is mentioned in the text.

#### `source`
* Extract the name of the media outlet or publication (e.g., 021.rs, Informer, N1, BBC). Infer if possible, otherwise use "unknown".

#### `date_of_news_issue`
* Date the news article was published. Use YYYY-MM-DD format ALWAYS. If DD.MM.YYYY format was used, convert it to YYYY-MM-DD. If mentioned explicitly or inferrable, extract it. Otherwise, use "unknown". (Note: The scraping part doesn't extract this automatically, rely on the text content).

#### `state_driven_messaging`
* Score from 0 to 10 indicating how much the article aligns with or promotes a **government or state narrative**, particularly regarding protests or student actions:
  * 0 = Neutral or objective reporting, no evident state influence.
  * 5 = Balanced reporting but subtly favors state perspective or uses state-preferred terminology.
  * 10 = Strongly biased in favor of government actions, dismissive or hostile toward protests/students, uses loaded language favoring the state.

#### `pro_student_messaging`
* Score from 0 to 10 indicating how much the article supports, sympathizes with, or positively portrays student protesters or their cause:
  * 0 = Hostile, dismissive, or negative portrayal of students/protests.
  * 5 = Neutral or balanced portrayal, presents student views fairly.
  * 10 = Strong support for the student cause, sympathetic portrayal, highlights positive aspects of student actions.

#### `student_mentions.good_count`
* Number of times students or student groups are portrayed **positively** (e.g., brave, organized, peaceful, justified, legitimate demands). Default to 0 if none.

#### `student_mentions.bad_count`
* Number of times students or student groups are portrayed **negatively** (e.g., violent, naive, manipulated, disruptive, illegitimate). Default to 0 if none.

#### `state_mentions.good_count`
* Number of times the government, state institutions, or authorities are portrayed **positively** (e.g., maintaining order, acting responsibly, dialogue-oriented). Default to 0 if none.

#### `state_mentions.bad_count`
* Number of times the government, state institutions, or authorities are portrayed **negatively** (e.g., oppressive, violent, corrupt, unresponsive, heavy-handed). Default to 0 if none.

#### `propaganda_count`
* Number of times one of the following words, or any form of those words or phrases in serbian (plural-singular, cases (nominativ, akuzativ, ....)) are mentioned: "blokaderi", "blokaderski", "ustaše", "boljševici", "plenum", "plenumaši", "blokaderska", "blokadera", "plenumaša", "plenumašu", "blokaderu", "obojena", "revolucija", "obojenu", "revoluciju", "obojene", "revolucije", "obojena revolucija", "vučić", "predsednik" or similar. If the source is 021.rs this has to be 0, otherwise, if the source is informer, count the occurences.

#### `pro_protest_count`
* Number of times one of the following words, or any form of those words or phrases in serbian (plural-singular, cases (nominativ, akuzativ, ....)) are mentioned: "blokada", "protest", "zahtevi", "studenti", "plenum", "student", "javni čas", "šetnja", "tura", "biciklisti", "demonstracija", "odavanje pošte" or similar. If the source is informer.rs this has to be 0, otherwise, if the source is 021, count the occurences.

---

### Input Text

You will receive a news article as raw text (scraped from a webpage). Your task is to read and analyze it thoroughly and then return the JSON structure above with accurate values and scores based *only* on the provided text. If a piece of information is not present in the text, use "unknown" for strings or `null` for numbers/booleans where specified (or 0 for counts).

---

Text to analyse: "{text_to_analyze}"

---

Always escape quotations in strings and ensure the output is valid JSON. Only output the JSON object, without any introductory text or markdown formatting like ```json.
JSON Output:
"""

    if not text_to_analyze:
        print("Error: No text provided for analysis.")
        return None

    try:
        response = model.generate_content(prompt)
        
        # Debug: Print raw response
        # print("--- Raw Gemini Response ---")
        # print(response.text)
        # print("--- End Raw Gemini Response ---")

        # Attempt to clean the response and parse JSON
        cleaned_response = response.text.strip()
        # Remove potential markdown backticks and language identifier
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[len("```json"):].strip()
        if cleaned_response.startswith("```"):
             cleaned_response = cleaned_response[len("```"):].strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-len("```")].strip()

        extracted_data = json.loads(cleaned_response)

        # --- Basic Validation based on *updated* expected structure ---
        if not isinstance(extracted_data, dict):
            print(f"Error: Expected a JSON object (dict), but got type {type(extracted_data)}")
            return None

        # Check for top-level keys defined in the prompt
        expected_top_keys = [
            "analysis", "source", "date_of_news_issue", "state_driven_messaging",
            "pro_student_messaging", "student_mentions", "state_mentions"
        ]
        missing_keys = [key for key in expected_top_keys if key not in extracted_data]
        if missing_keys:
            # This might be too strict if Gemini sometimes fails to find info,
            # but it's good for ensuring the structure is generally followed.
            print(f"Warning: Missing expected top-level keys in JSON response: {missing_keys}")
            # Consider if you want to return None or proceed with partial data
            # return None

        # Deeper validation (optional, but good practice)
        if "analysis" in extracted_data and not isinstance(extracted_data["analysis"], dict):
             print(f"Warning: 'analysis' field is not a dictionary.")
        if "student_mentions" in extracted_data and not isinstance(extracted_data["student_mentions"], dict):
             print(f"Warning: 'student_mentions' field is not a dictionary.")
        if "state_mentions" in extracted_data and not isinstance(extracted_data["state_mentions"], dict):
             print(f"Warning: 'state_mentions' field is not a dictionary.")
        # Add more checks as needed (e.g., for types of scores, counts)

        return extracted_data

    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from response.")
        print(f"JSONDecodeError: {e}")
        print(f"Cleaned response was: {cleaned_response}")
        return None
    except AttributeError:
         # Handle cases where response.text might not exist (e.g., API error response)
         print(f"Error: Could not get text from the API response. Response object: {response}")
         # Try to access parts for more info, handling potential errors
         try:
             print(f"Prompt Feedback: {response.prompt_feedback}")
             print(f"Candidates: {response.candidates}")
         except Exception as feedback_err:
             print(f"Could not retrieve detailed feedback: {feedback_err}")
         return None
    except Exception as e:
        # Catch potential errors during API call itself or other unexpected issues
        print(f"An error occurred during Gemini API call or processing: {e}")
        try:
            # Attempt to print response text for debugging if available
            if hasattr(response, 'text'):
                 print(f"Raw response content: {response.text}")
            else:
                 print(f"Response object details: {response}")
        except Exception:
            pass # Ignore if response details are not available
        return None

# --- Main Execution Block ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape an article from 021.rs or informer.rs and analyze its text using Gemini.")
    parser.add_argument("--url", required=True, help="The URL of the article to scrape and analyze.")
    parser.add_argument("--source", required=True, choices=['021.rs', 'informer.rs'], help="The source website (either '021.rs' or 'informer.rs').")

    args = parser.parse_args()

    print(f"Attempting to scrape article from: {args.url} (Source: {args.source})")
    scraped_text = scrape_article_text(args.url, args.source)

    if scraped_text:
        print(f"Successfully scraped {len(scraped_text)} characters.")
        # Optional: Print first few characters of scraped text for verification
        # print("--- Scraped Text (Preview) ---")
        # print(scraped_text[:500] + "...")
        # print("--- End Scraped Text Preview ---")

        print("\nAnalyzing scraped text with Gemini...")
        analysis_result = analyze_text_sentiment(scraped_text)

        if analysis_result:
            print("\n--- Gemini Analysis Result ---")
            # Pretty print the JSON output
            print(json.dumps(analysis_result, indent=2, ensure_ascii=False)) # ensure_ascii=False for non-Latin chars
            print("--- End Analysis Result ---")
        else:
            print("\nAnalysis failed. Check logs for errors.")
            # Consider saving the scraped text to a file for manual inspection
            # with open("scraped_text_for_debug.txt", "w", encoding="utf-8") as f:
            #    f.write(scraped_text)
            # print("Scraped text saved to scraped_text_for_debug.txt")

    else:
        print("\nScraping failed. Cannot proceed with analysis.")

    # --- Old example usage removed as the script now requires URL input ---
    # print("Analyzing sample text...")
    # analysis_result = analyze_text_sentiment(sample_article_text) # sample_article_text no longer defined here
    # ... etc ...