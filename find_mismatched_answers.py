import json
import re

def find_mismatched_questions(file_path):
    """
    Finds questions that contain 'Choose two' but don't have multiple correct answers.
    """
    print(f"--- Checking {file_path} ---")
    mismatched_count = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for i, q in enumerate(data):
            question_text = q.get('question_text', '')
            correct_answer = q.get('correct_answer', '')
            question_id = q.get('question_id', f'index_{i}')

            # Check if "Choose two" is in the question text (case-insensitive)
            if re.search(r'\(Choose two\.\)', question_text, re.IGNORECASE):
                # Check if the correct_answer field lacks a comma
                if ',' not in correct_answer:
                    mismatched_count += 1
                    print(f"  [MISMATCH] Question ID: {question_id}")
                    print(f"    Text: {question_text[:100]}...")
                    print(f"    Correct Answer: '{correct_answer}' (Expected multiple answers)")
                    print("-" * 20)

        if mismatched_count == 0:
            print("No mismatched questions found.")
        else:
            print(f"Found {mismatched_count} mismatched questions.")

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
    print()


if __name__ == '__main__':
    find_mismatched_questions('qa_parsed.json')
    find_mismatched_questions('pde_parsed.json')
