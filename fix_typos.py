import json
import re

def clean_text(text):
    if not text:
        return text
    
    # Replace weird characters
    text = text.replace('ג€', '"')
    text = text.replace('˜', "'")
    text = text.replace('\u2028', ' ')
    text = text.replace('\u200b', '')
    
    # Fix unnecessary spaces before punctuation
    text = re.sub(r'\s+([,\.\?\!])', r'\1', text)
    
    # Fix missing spaces after punctuation, but exclude acronyms, URLs, decimals
    # Exclude situations like "e.g.", "i.e.", "U.S.", "v1.0", "Node.js", etc.
    # We only add a space if followed by a Capital letter or another word but not if it looks like an acronym or domain.
    # Simple heuristic: Period followed by uppercase letter without space.
    text = re.sub(r'([a-z])\.([A-Z])', r'\1. \2', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Fix typo patterns if any common ones exist
    text = text.replace('neutral-network', 'neural network')
    text = text.replace('featuers', 'features')
    text = text.replace('continuos', 'continuous')
    
    return text.strip()

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        # Clean question text
        item['question_text'] = clean_text(item.get('question_text', ''))
        
        # Clean options
        if 'options' in item:
            for k, v in item['options'].items():
                item['options'][k] = clean_text(v)
                
        # Format correct answer (e.g. "AB" -> "A, B" if it's multiple choice)
        ans = item.get('correct_answer', '').replace(' ', '')
        if len(ans) > 1 and ',' not in ans:
            # check if it's something like "AD" -> "A, D"
            if re.match(r'^[A-Z]{2,5}$', ans):
                item['correct_answer'] = ', '.join(list(ans))
        
        # Also clean discussion & comments text but preserve HTML structure
        item['discussion_and_comments'] = clean_text(item.get('discussion_and_comments', ''))

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    process_file('qa_parsed.json')
    process_file('pde_parsed.json')
    print("Typos fixed and spaces removed.")
