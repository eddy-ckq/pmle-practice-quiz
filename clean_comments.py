import json
import re

def clean_comments(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for q in data:
        text = q.get('discussion_and_comments', '')
        if not text:
            continue
            
        text = re.sub(r'^Comments\s*', '', text)
        text = re.sub(r'[A-Za-z0-9_.-]+\s+(?:Highly Voted\s+|Most Recent\s+)?\d+\s+(?:years?|months?|weeks?|days?|hours?)(?:, \d+ (?:years?|months?|weeks?|days?|hours?))?\s+ago', '\\n- ', text)
        text = re.sub(r'upvoted \d+ times', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Selected Answer:\s*[A-Z, ]+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<br><br><b><u>Correct Answer:.*?<b>Community vote distribution</b>.*?(?:\\n|$)', '\\n', text, flags=re.IGNORECASE)
        text = re.sub(r'\\n+', '\\n', text)
        text = re.sub(r' +', ' ', text)
        
        q['discussion_and_comments'] = text.strip()
        
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

clean_comments('qa_parsed.json')
clean_comments('pde_parsed.json')
