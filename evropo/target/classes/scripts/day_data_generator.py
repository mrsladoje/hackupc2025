import json
import os
from collections import defaultdict

def aggregate_daily_data(input_jsonl_path, output_jsonl_path):
    """
    Reads a JSONL file containing news article analyses, aggregates data per day,
    and writes the daily summaries to a new JSONL file.

    Each output line summarizes student mentions (by source and sentiment),
    state-driven messaging counts, and protest mention counts for a single day.

    Args:
        input_jsonl_path (str): Path to the input JSONL file.
        output_jsonl_path (str): Path to the output JSONL file to be created.
    """
    # Use defaultdict to easily initialize data for new dates
    daily_data = defaultdict(lambda: {
        "student_mentions": {
            "government": {"good": 0, "bad": 0},
            "independent": {"good": 0, "bad": 0}
        },
        "state_driven_messaging": 0,
        "protest_count": 0
    })

    try:
        with open(input_jsonl_path, 'r', encoding='utf-8') as infile:
            for line_num, line in enumerate(infile):
                try:
                    data = json.loads(line.strip())
                except json.JSONDecodeError:
                    print(f"Warning: Skipping invalid JSON on line {line_num + 1} in {input_jsonl_path}")
                    continue

                # --- Data Extraction ---
                # Adjust these keys based on your actual input JSON structure
                article_date = data.get("publish_date") # Assumes 'publish_date' key exists
                source_type = data.get("source_type") # Assumes 'source_type' ('government'/'independent')
                analysis = data.get("analysis", {})

                if not article_date:
                    # print(f"Warning: Skipping entry on line {line_num + 1} due to missing date.")
                    continue

                # --- Aggregation Logic ---
                day_stats = daily_data[article_date]

                # 1. Student Mentions
                # Assumes analysis contains 'mentions_students' (bool) and 'student_mention_sentiment' ('good'/'bad')
                if analysis.get("mentions_students"):
                    sentiment = analysis.get("student_mention_sentiment")
                    if source_type in ["government", "independent"] and sentiment in ["good", "bad"]:
                        day_stats["student_mentions"][source_type][sentiment] += 1
                    # else:
                        # Optional: Log warnings for missing/invalid source_type or sentiment if needed
                        # print(f"Warning: Invalid source ('{source_type}') or sentiment ('{sentiment}') for student mention on line {line_num + 1}")


                # 2. State-Driven Messaging (Propaganda Count)
                # Assumes analysis contains 'is_propaganda' (bool)
                if analysis.get("is_propaganda"): # Checks if the key exists and is True
                    day_stats["state_driven_messaging"] += 1

                # 3. Protest Count
                # Assumes analysis contains 'mentions_protest' (bool)
                if analysis.get("mentions_protest"): # Checks if the key exists and is True
                    day_stats["protest_count"] += 1

    except FileNotFoundError:
        print(f"Error: Input file not found at {input_jsonl_path}")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading the input file: {e}")
        return

    # --- Output Generation ---
    output_dir = os.path.dirname(output_jsonl_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            print(f"Error creating output directory {output_dir}: {e}")
            return

    try:
        with open(output_jsonl_path, 'w', encoding='utf-8') as outfile:
            # Sort data by date before writing
            for date, stats in sorted(daily_data.items()):
                output_record = {"date": date, **stats}
                json.dump(output_record, outfile)
                outfile.write('\n')
        print(f"Successfully aggregated daily data and saved to {output_jsonl_path}")
    except IOError as e:
        print(f"Error writing output file {output_jsonl_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while writing the output file: {e}")

# Example Usage (replace with your actual file paths)
if __name__ == "__main__":
    input_file = 'path/to/your/input_analyses.jsonl'
    output_file = 'path/to/your/daily_summary.jsonl'

    # Create a dummy input file for testing if needed
    if not os.path.exists(input_file):
        print(f"Creating dummy input file: {input_file}")
        os.makedirs(os.path.dirname(input_file), exist_ok=True)
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write('{"publish_date": "2024-01-15", "source_type": "government", "analysis": {"mentions_students": true, "student_mention_sentiment": "good", "is_propaganda": true, "mentions_protest": false}}\n')
            f.write('{"publish_date": "2024-01-15", "source_type": "independent", "analysis": {"mentions_students": true, "student_mention_sentiment": "bad", "is_propaganda": false, "mentions_protest": true}}\n')
            f.write('{"publish_date": "2024-01-16", "source_type": "government", "analysis": {"mentions_students": false, "is_propaganda": true, "mentions_protest": true}}\n')
            f.write('{"publish_date": "2024-01-15", "source_type": "government", "analysis": {"mentions_students": true, "student_mention_sentiment": "bad", "is_propaganda": true, "mentions_protest": true}}\n')
            f.write('{"publish_date": "2024-01-16", "source_type": "independent", "analysis": {"mentions_students": true, "student_mention_sentiment": "good", "is_propaganda": false, "mentions_protest": false}}\n')
            f.write('{"publish_date": "2024-01-15", "source_type": "unknown", "analysis": {"mentions_students": true, "student_mention_sentiment": "good"}}\n') # Test invalid source
            f.write('{"publish_date": "2024-01-15", "source_type": "independent"}\n') # Test missing analysis keys

    aggregate_daily_data(input_file, output_file)

    # Optional: Print output file content for verification
    if os.path.exists(output_file):
        print(f"\n--- Content of {output_file} ---")
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                print(line.strip())
        print("----------------------------")