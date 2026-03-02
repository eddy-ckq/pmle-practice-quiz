import json
import argparse
import os

def find_first_incomplete(file_path):
    """
    Scans a JSON file to find the index of the first question
    that does not have a 'Gemini Deep Dive Explanation'.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing {file_path}: {e}")
        return -1, 0

    total_incomplete = 0
    first_incomplete_index = -1

    for i, q in enumerate(data):
        explanation = q.get('ai_explanation', '')
        if "Gemini Deep Dive Explanation" not in explanation:
            total_incomplete += 1
            if first_incomplete_index == -1:
                first_incomplete_index = i
    
    return first_incomplete_index, total_incomplete

def main():
    parser = argparse.ArgumentParser(description="Find questions with incomplete AI explanations.")
    parser.add_argument('files', nargs='+', help='The JSON file(s) to process (e.g., qa_parsed.json pde_parsed.json).')
    
    args = parser.parse_args()

    print("--- Scanning for incomplete explanations ---")
    for file_path in args.files:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue

        first_index, total_count = find_first_incomplete(file_path)

        if total_count > 0:
            print(f"\nFile: {file_path}")
            print(f"  Found {total_count} questions with old explanations.")
            print(f"  The first incomplete question is at index: {first_index}")
            print(f"  To fix this, run: python generate_deep_explanations.py --file {file_path} --start_index {first_index}")
        else:
            print(f"\nFile: {file_path}")
            print("  All explanations seem to be upgraded. No action needed.")
    print("\n--- Scan complete ---")

if __name__ == '__main__':
    main()
