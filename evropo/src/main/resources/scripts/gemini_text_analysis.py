import google.generativeai as genai
import os
import json
import argparse

# Configure the Gemini API key
# Make sure to set the GOOGLE_API_KEY environment variable
# or replace os.getenv("GOOGLE_API_KEY") with your actual key.

GOOGLE_API_KEY = 'halal'

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    # genai.configure(api_key=os.getenv(GOOGLE_API_KEY))
except TypeError:
    print("Error: GOOGLE_API_KEY environment variable not set.")
    exit(1)

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

def analyze_text_sentiment(text_to_analyze):
    """
    Analyzes the input text using the Gemini API to extract sentiment scores.

    Args:
        text_to_analyze: The string containing the text to analyze.

    Returns:
        A dictionary containing the scores in JSON format,
        or None if an error occurs.
    """

    prompt = f"""

You are an advanced text analysis model. Your task is to analyze the following article about a student protest and return a structured JSON output containing specific metrics.

Use the structure and detailed explanation below to perform your analysis accurately:

---

### **JSON Output Structure and Field Descriptions**


''' JSON

    "analysis": {{
        "mentions_protest": true | false,
        "protest_info": {{
            "organizer": "Name or group organizing the protest, if mentioned",
            "date": "Date of the protest (not the article publication date), in YYYY-MM-DD format if possible",
            "location": "City or area where the protest is occurring",
            "count": {{
                "government": Number | null, // Estimated crowd size according to pro-government sources
                "independent": Number | null // Estimated crowd size according to independent sources
            }}
        }}
    }},
    "source": "Name of the publication or source (e.g., BBC, Reuters, state-run outlet)",
    "date_of_news_issue": "Date when this article was published, in YYYY-MM-DD format",
    "state_driven_messaging": Integer between 0 and 5,
    "pro_student_messaging": Integer between 0 and 5,
    "student_mentions": {{
        "good_count": Number of times students are mentioned positively,
        "bad_count": Number of times students are mentioned negatively
    }},
    "state_mentions": {{
        "good_count": Number of times the government/state is mentioned positively,
        "bad_count": Number of times the government/state is mentioned negatively
    }}

'''

---

### Explanation of Each Metric

#### `analysis.mentions_protest`

* Return `true` if the article directly references a protest or demonstration.
* Return `false` if no protest is mentioned.

#### `analysis.protest_info.organizer`

* Name the individual(s), student group, political group, or organization responsible for organizing the protest. If not mentioned, use "unknown".

#### `analysis.protest_info.date`

* Extract the actual date of the protest as stated in the article, not the date of publication. Use YYYY-MM-DD format if possible. If not mentioned, use "unknown".

#### `analysis.protest_info.location`

* Provide the geographical location where the protest took place. If not mentioned, use "unknown".

#### `analysis.protest_info.count.government`

* Extract the **estimated number of people** attending the protest *as reported by government or pro-government sources*.
* Return the number as an integer if found.
* Return `null` if no such estimate from a government source is mentioned in the text.

#### `analysis.protest_info.count.independent`

* Extract the **estimated number of people** attending the protest *as reported by independent sources* (e.g., organizers, independent media, observers).
* Return the number as an integer if found.
* Return `null` if no such estimate from an independent source is mentioned in the text.

#### `source`

* Extract the name of the media outlet or publication (e.g., CNN, Al Jazeera, China Daily). If not mentioned, use "unknown".

#### `date_of_news_issue`

* Date the news article was published. Use YYYY-MM-DD format if possible. If not mentioned, use "unknown".

#### `state_driven_messaging`

* Score from 0 to 5 indicating how much **government or state propaganda** is present:

  * 0 = No government narrative present
  * 5 = Strongly biased in favor of government or hostile toward protests

#### `pro_student_messaging`

* Score from 0 to 5 indicating how much the article supports or sympathizes with student protesters:

  * 0 = Hostile or dismissive toward students
  * 5 = Strong support for the student cause or sympathetic portrayal

#### `student_mentions.good_count`

* Number of times students are portrayed **positively** (e.g., brave, organized, peaceful, idealistic)

#### `student_mentions.bad_count`

* Number of times students are portrayed **negatively** (e.g., violent, naïve, manipulated, disruptive)

#### `state_mentions.good_count`

* Number of times the government or state institutions are portrayed **positively** (e.g., maintaining order, acting responsibly)

#### `state_mentions.bad_count`

* Number of times the government or state institutions are portrayed **negatively** (e.g., oppressive, violent, corrupt)

---

### Input Text

You will receive a news article as raw text. Your task is to read and analyze it thoroughly and then return the JSON structure above with accurate values and scores based *only* on the provided text. If a piece of information is not present in the text, use "unknown" for strings or `null` for numbers where specified.

---

Text to analyse: "{text_to_analyze}"

---

Always escape quotations in strings and ensure the output is valid JSON. Only output the JSON object, without any introductory text or markdown formatting like ```json.
JSON Output:
"""

    try:
        response = model.generate_content(prompt)
        # Attempt to clean the response and parse JSON
        # Gemini might sometimes include markdown backticks or 'json' label
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()

        extracted_data = json.loads(cleaned_response)

        # Basic validation - check if it's a dictionary and has expected keys
        if not isinstance(extracted_data, dict):
            print(f"Error: Expected a JSON object, but got type {type(extracted_data)}")
            return None

        expected_keys = [
            "event_date", "main_location", "organizers", "estimated_crowd_size",
            "protest_cause", "demands_or_goals", "sentiment_towards_protest",
            "violence_level", "authority_response", "outcome_or_resolution"
        ]

        missing_keys = [key for key in expected_keys if key not in extracted_data]
        if missing_keys:
            print(f"Error: Missing expected keys in JSON response: {missing_keys}")
            # Allow processing even if some keys are missing, as per prompt's "unknown" rule
            # The consumer of this function should handle potentially missing keys or "unknown" values.
            # return None # Commented out to be less strict

        # Further validation based on prompt rules (optional but recommended)
        organizers_val = extracted_data.get("organizers")
        if organizers_val not in ["students", "government", "other"]:
             print(f"Warning: 'organizers' field ('{organizers_val}') is not one of the expected values ('students', 'government', 'other').")
             # Decide if this should be a hard failure or just a warning
             # return None # Uncomment to enforce strictly

        if not isinstance(extracted_data.get("demands_or_goals"), list):
             print(f"Warning: 'demands_or_goals' field is not a list.")
             # return None # Uncomment to enforce strictly

        if not isinstance(extracted_data.get("authority_response"), list):
             print(f"Warning: 'authority_response' field is not a list.")
             # return None # Uncomment to enforce strictly

        # If basic structure is okay, return the extracted data
        return extracted_data

    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from response: {cleaned_response}")
        return None
    except AttributeError:
         # Handle cases where response.text might not exist (e.g., API error response)
         print(f"Error: Could not get text from the API response. Response: {response}")
         return None
    except Exception as e:
        # Catch potential errors during API call itself or other unexpected issues
        print(f"An error occurred during API call or processing: {e}")
        try:
            # Attempt to print response text for debugging if available
            print(f"Raw response content: {response.text}")
        except Exception:
            pass # Ignore if response or response.text is not available
        return None


# # Example usage:
# if __name__ == "__main__":
#     # Sample text for analysis (replace with actual article text)
#     sample_article_text = """
#     BEIJING, June 5, 1989 (Reuters) - Hundreds of students gathered in Tiananmen Square yesterday, continuing protests demanding democratic reforms.
#     Organized primarily by student federations, the demonstration began peacefully on June 4th.
#     Independent observers estimate the crowd size peaked at around 100,000, while state media reported significantly lower numbers, around 10,000, calling the protesters 'rioters'.
#     The government, portrayed by official news outlets like China Daily as maintaining stability, has warned against further unrest.
#     Student leaders expressed frustration, calling the government's response heavy-handed and oppressive. They demand dialogue.
#     Pro-student voices highlight the peaceful nature of the initial gathering, while state-run media focuses on isolated incidents of violence, blaming students.
#     The article was published on June 5, 1989.
#     """

#     print("Analyzing sample text...")
#     analysis_result = analyze_text_sentiment(sample_article_text)

#     if analysis_result:
#         print("\nAnalysis successful:")
#         # Pretty print the JSON output
#         print(json.dumps(analysis_result, indent=2))
#     else:
#         print("\nAnalysis failed.")

#     # Example with text NOT mentioning a protest
#     non_protest_text = """
#     LONDON, October 26, 2023 (BBC News) - The UK government announced new economic policies today aimed at curbing inflation.
#     The Chancellor detailed the plans in Parliament. Financial markets reacted mildly.
#     This report was published on 2023-10-26.
#     """
#     print("\nAnalyzing non-protest text...")
#     analysis_result_non_protest = analyze_text_sentiment(non_protest_text)

#     if analysis_result_non_protest:
#         print("\nAnalysis successful:")
#         print(json.dumps(analysis_result_non_protest, indent=2))
#     else:
#         print("\nAnalysis failed.")