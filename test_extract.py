import json
import re

def extract_wrong_reasoning(discussion, target_letter):
    if not discussion:
        return ''
    
    lines = [line.strip() for line in discussion.split('\\n') if line.strip()]
    
    # 1. Look for explicit rejection: 'not A', 'A is wrong', 'A is incorrect', 'A is false'
    pattern1 = r'(?i)(\\bnot\s*' + target_letter + r'\\b|\\b' + target_letter + r'\s*is wrong|\\b' + target_letter + r'\s*is incorrect|\\b' + target_letter + r'\s*is false|why not\s*' + target_letter + r'\\b)'
    for line in lines:
        if re.search(pattern1, line) and len(line.split()) > 5:
            clean_line = re.sub(r'^-?\s*(?:Selected Answer:\s*[A-Z, ]+)?\s*', '', line, flags=re.IGNORECASE)
            return clean_line

    # 2. Look for lines like A: ... explaining it
    pattern2 = r'(?i)(^|\s|-)' + target_letter + r'\s*:'
    for line in lines:
        if re.search(pattern2, line) and len(line.split()) > 5:
            clean_line = re.sub(r'^-?\s*(?:Selected Answer:\s*[A-Z, ]+)?\s*', '', line, flags=re.IGNORECASE)
            return clean_line

    return ''

with open('pde_parsed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for q in data[:20]:
    disc = q.get('discussion_and_comments', '')
    print(f'Q: {q.get("question_id")}')
    for opt in q.get('options', {}).keys():
        if opt not in q.get('correct_answer', ''):
            reason = extract_wrong_reasoning(disc, opt)
            if reason:
                print(f'  {opt}: {reason}')
