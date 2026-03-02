import json
import re

def flag_mismatched_questions(file_path):
    """
    Finds questions that contain 'Choose two' but don't have multiple correct answers,
    and adds a 'needs_review' flag to them.
    """
    print(f"--- Processing {file_path} ---")
    flagged_count = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for i, q in enumerate(data):
            question_text = q.get('question_text', '')
            correct_answer = q.get('correct_answer', '')

            if re.search(r'\(Choose two\.\)', question_text, re.IGNORECASE):
                if ',' not in correct_answer:
                    q['needs_review'] = True
                    flagged_count += 1
                    print(f"  [FLAGGED] Question ID: {q.get('question_id', f'index_{i}')}")

        if flagged_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Successfully flagged {flagged_count} questions for review.")
        else:
            print("No questions needed flagging.")

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
    print()

if __name__ == '__main__':
    flag_mismatched_questions('qa_parsed.json')
    flag_mismatched_questions('pde_parsed.json')
