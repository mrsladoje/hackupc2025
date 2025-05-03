import json
import os

def extract_protests(input_jsonl_path, output_jsonl_path):
    """
    Reads a JSONL file containing news article analyses, identifies unique protests
    (based on date and location), aggregates information about them, and writes
    the consolidated protest data to a new JSONL file.

    Args:
        input_jsonl_path (str): Path to the input JSONL file.
        output_jsonl_path (str): Path to the output JSONL file to be created.
    """
    protests = {}  # Dictionary to store unique protests: {(date, location): protest_data}

    try:
        with open(input_jsonl_path, 'r', encoding='utf-8') as infile:
            for line_num, line in enumerate(infile):
                try:
                    data = json.loads(line.strip())
                except json.JSONDecodeError:
                    print(f"Warning: Skipping invalid JSON on line {line_num + 1} in {input_jsonl_path}")
                    continue

                analysis = data.get("analysis", {})
                if analysis.get("mentions_protest"):
                    protest_info = analysis.get("protest_info", {})
                    protest_date = protest_info.get("date")
                    protest_location = protest_info.get("location")
                    protest_organizer = protest_info.get("organizer")
                    protest_counts = protest_info.get("count", {})
                    gov_count = protest_counts.get("government")
                    ind_count = protest_counts.get("independent")

                    # Basic validation: date and location are required to identify a unique protest
                    if not protest_date or not protest_location:
                        # print(f"Warning: Skipping entry on line {line_num + 1} due to missing date or location.")
                        continue

                    protest_key = (protest_date, protest_location)

                    if protest_key not in protests:
                        protests[protest_key] = {
                            "date": protest_date,
                            "location": protest_location,
                            "organizer": None, # Initialize organizer
                            "count": {"government": None, "independent": None}
                        }

                    # Update organizer if not already set or if the current one is more specific (optional logic)
                    # Simple approach: take the first non-empty organizer found
                    if not protests[protest_key]["organizer"] and protest_organizer:
                         protests[protest_key]["organizer"] = protest_organizer
                    # More complex logic could be added here if needed (e.g., merging organizers)


                    # Update counts - take the first non-null value encountered for each type
                    if protests[protest_key]["count"]["government"] is None and gov_count is not None:
                        try:
                            protests[protest_key]["count"]["government"] = int(gov_count)
                        except (ValueError, TypeError):
                             print(f"Warning: Invalid government count '{gov_count}' on line {line_num + 1}. Skipping count update.")


                    if protests[protest_key]["count"]["independent"] is None and ind_count is not None:
                         try:
                            protests[protest_key]["count"]["independent"] = int(ind_count)
                         except (ValueError, TypeError):
                             print(f"Warning: Invalid independent count '{ind_count}' on line {line_num + 1}. Skipping count update.")


    except FileNotFoundError:
        print(f"Error: Input file not found at {input_jsonl_path}")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading the input file: {e}")
        return

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_jsonl_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Write the aggregated protest data to the output JSONL file
    try:
        with open(output_jsonl_path, 'w', encoding='utf-8') as outfile:
            for protest_data in protests.values():
                json.dump(protest_data, outfile)
                outfile.write('\n')
        print(f"Successfully processed protests and saved to {output_jsonl_path}")
    except IOError as e:
        print(f"Error writing output file {output_jsonl_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing the output file: {e}")


if __name__ == '__main__':
    # Example Usage:
    # Create a dummy input file for testing
    dummy_input_data = [
        {
            "analysis": {
                "mentions_protest": True,
                "protest_info": {
                    "organizer": "Students Union",
                    "date": "2024-03-15",
                    "location": "Capital City",
                    "count": {"government": 5000, "independent": None}
                }
            },
            "source": "State News Agency",
            "date_of_news_issue": "2024-03-16",
            "state_driven_messaging": 4,
            "pro_student_messaging": 1,
            "student_mentions": {"good_count": 1, "bad_count": 5},
            "state_mentions": {"good_count": 6, "bad_count": 0}
        },
        {
            "analysis": {
                "mentions_protest": True,
                "protest_info": {
                    "organizer": "Student Activists", # Different organizer, same protest
                    "date": "2024-03-15",
                    "location": "Capital City",
                    "count": {"government": None, "independent": 8000}
                }
            },
            "source": "Independent Observer",
            "date_of_news_issue": "2024-03-16",
            "state_driven_messaging": 1,
            "pro_student_messaging": 4,
            "student_mentions": {"good_count": 7, "bad_count": 1},
            "state_mentions": {"good_count": 1, "bad_count": 2}
        },
         {
            "analysis": {
                "mentions_protest": True,
                "protest_info": {
                    "organizer": "Civic Group",
                    "date": "2024-04-01",
                    "location": "Second City",
                    "count": {"government": None, "independent": 1500}
                }
            },
            "source": "Local Paper",
            "date_of_news_issue": "2024-04-02",
             "state_driven_messaging": 2,
            "pro_student_messaging": 3,
            "student_mentions": {"good_count": 3, "bad_count": 0},
            "state_mentions": {"good_count": 2, "bad_count": 1}
        },
        {
            "analysis": { # Article not mentioning protest
                "mentions_protest": False,
                "protest_info": {}
            },
            "source": "Financial Times",
            "date_of_news_issue": "2024-03-17",
            "state_driven_messaging": 1,
            "pro_student_messaging": 0,
             "student_mentions": {"good_count": 0, "bad_count": 0},
            "state_mentions": {"good_count": 1, "bad_count": 0}
        },
         { # Article mentioning protest but missing location
            "analysis": {
                "mentions_protest": True,
                "protest_info": {
                    "organizer": "Anonymous",
                    "date": "2024-05-10",
                    "location": None, # Missing location
                    "count": {"government": 100, "independent": 150}
                }
            },
            "source": "Blog Post",
            "date_of_news_issue": "2024-05-11",
             "state_driven_messaging": 0,
            "pro_student_messaging": 5,
            "student_mentions": {"good_count": 5, "bad_count": 0},
            "state_mentions": {"good_count": 0, "bad_count": 3}
        }
    ]

    input_file = "../../../../../../../OneDrive/Documents/Barcelona_HackUPC_2025/Grafana/dummy_gemini_output.jsonl"
    output_file = "../../../../../../../OneDrive/Documents/Barcelona_HackUPC_2025/Grafana/aggregated_protests.jsonl"

    # Create the dummy input file
    with open(input_file, 'w', encoding='utf-8') as f:
        for item in dummy_input_data:
            json.dump(item, f)
            f.write('\n')

    print(f"Created dummy input file: {input_file}")

    # Run the extraction function
    extract_protests(input_file, output_file)

    # Optional: Print the contents of the output file
    if os.path.exists(output_file):
        print(f"\nContents of {output_file}:")
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                print(line.strip())

    # Clean up dummy files
    # os.remove(input_file)
    # os.remove(output_file)
    # print("\nCleaned up dummy files.")