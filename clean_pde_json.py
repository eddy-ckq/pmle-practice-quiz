import json
import re

def clean_data():
    with open('pde_parsed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_data = []
    for i, q in enumerate(data):
        q['question_id'] = str(i + 1)
        
        q_text = q['question_text']
        
        # Strip case study text
        if q.get('case_study'):
            parts = q_text.split('CFO Statement -')
            if len(parts) > 1:
                cfo_and_question = parts[1]
                lines = cfo_and_question.split('\n')
                for j, line in enumerate(lines):
                    if 'environment.' in line or 'pipelines.' in line:
                        q_text = '\n'.join(lines[j+1:]).strip()
                        break
        
        # Remove "Question:" at the start
        q_text = re.sub(r'^\s*(?:Question:)?\s*', '', q_text, flags=re.IGNORECASE)
        q['question_text'] = q_text.strip()
        
        cleaned_data.append(q)

    with open('pde_parsed.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        
    print(f"Cleaned {len(cleaned_data)} questions.")

if __name__ == '__main__':
    clean_data()
