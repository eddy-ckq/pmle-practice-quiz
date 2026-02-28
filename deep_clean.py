import json
import re

def aggressive_clean(text):
    if not text:
        return text
    
    # Remove HTML tags completely
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Remove "Correct Answer: X" block if it came from the community distribution text
    text = re.sub(r'Correct Answer:\s*[A-Z]\s*', '', text, flags=re.IGNORECASE)
    
    # Remove "Community vote distribution" blocks
    text = re.sub(r'Community vote distribution\s*.*?(?:\\n|$)', '\\n', text, flags=re.IGNORECASE)
    
    # Remove trailing "... " or weird suffixes
    text = re.sub(r'\.{3,}$', '...', text)
    text = re.sub(r'\s+[A-Za-z0-9_.-]+\.\.\.$', '...', text) # catches things like " jkkim..."
    
    # Remove stray "y y" or "y " at the end of lines
    text = re.sub(r'\s+y\s+y(?:\\n|$)', '\\n', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple newlines with a single newline
    text = re.sub(r'\\n+', '\\n', text)
    
    # Remove lines that are just "-"
    lines = [line.strip() for line in text.split('\\n')]
    lines = [line for line in lines if line and line != '-']
    
    return '\\n'.join(lines).strip()

def process(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for q in data:
        text = q.get('discussion_and_comments', '')
        if text:
            cleaned = aggressive_clean(text)
            q['discussion_and_comments'] = cleaned
            
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

process('qa_parsed.json')
process('pde_parsed.json')
print("Successfully deep cleaned comments.")
