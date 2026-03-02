import json

def update_question(file_path, question_id, new_answer):
    """
    Updates a specific question in a JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        found = False
        for q in data:
            if q.get('question_id') == question_id:
                q['correct_answer'] = new_answer
                if 'needs_review' in q:
                    del q['needs_review']
                found = True
                break
        
        if found:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Successfully updated question {question_id} in {file_path}")
        else:
            print(f"Question {question_id} not found in {file_path}")

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")

if __name__ == '__main__':
    # Correcting PDE questions
    update_question('pde_parsed.json', '217', 'B, E')
    update_question('pde_parsed.json', '228', 'B, E')
    update_question('pde_parsed.json', '231', 'C, D')
