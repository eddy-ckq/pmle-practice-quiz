import json
import re
import sys

def clean_text(text):
    if not text:
        return text
    # Replace multiple spaces or newlines with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def format_comments(comments):
    if not comments:
        return comments
    
    # First, let's normalize some common headers
    comments = re.sub(r'^Comments\\n', '', comments, flags=re.IGNORECASE)
    
    # Let's add some line breaks around "Correct Answer:"
    comments = re.sub(r'(Correct Answer:\s*[A-Z, ]+)', r'<br><br><b><u>\1</u></b><br>', comments, flags=re.IGNORECASE)
    comments = re.sub(r'(Community vote distribution)', r'<br><b>\1</b>', comments, flags=re.IGNORECASE)
    
    # Split the remaining text into lines to process comments
    lines = comments.split('\\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line is a comment header: e.g., "esuaaaa Highly Voted 4 years, 8 months ago"
        header_match = re.search(r'^(.*?)\s+((?:Highly Voted\s+)?(?:Most Recent\s+)?\d+ (?:year|month|week|day|hour)s?(?:, \d+ (?:year|month|week|day|hour)s?)? ago)$', line)
        
        # Check if line is upvote: "upvoted 26 times"
        upvote_match = re.search(r'^upvoted (\d+) times', line, flags=re.IGNORECASE)
        
        # Check if line is just "A (100%)" or "y" (often junk from scraping)
        vote_dist_match = re.match(r'^[A-Z]\s*\(\d+%\)$', line)
        
        if header_match:
            user = header_match.group(1).strip()
            time_info = header_match.group(2).strip()
            formatted_lines.append(f"<br><b>{user}</b> <u>[{time_info}]</u>:<br>")
        elif upvote_match:
            formatted_lines.append(f"<i>(Upvoted {upvote_match.group(1)} times)</i><br><br>")
        elif vote_dist_match:
            formatted_lines.append(f"&bull; {line}<br>")
        elif line == 'y' or line == 'Select Answer:':
            continue
        elif line.startswith('Selected Answer:'):
            formatted_lines.append(f"<b>Selected Answer:</b> {line.replace('Selected Answer:', '').strip()}<br>")
        elif 'Correct Answer:' in line and '<br>' in line:
             formatted_lines.append(line) # already formatted
        elif 'Community vote distribution' in line and '<br>' in line:
             formatted_lines.append(line) # already formatted
        else:
            # Regular text
            formatted_lines.append(f"{line}<br>")
            
    # Join everything and clean up multiple <br>
    result = "".join(formatted_lines)
    result = re.sub(r'(<br>\s*){3,}', '<br><br>', result)
    return result

def process_file(file_path):
    print(f"Processing {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    for item in data:
        # 1. Clean question_text
        item['question_text'] = clean_text(item.get('question_text', ''))
        
        # 2. Clean options
        if 'options' in item:
            for k, v in item['options'].items():
                item['options'][k] = clean_text(v)
                
        # 3. Format discussion_and_comments
        item['discussion_and_comments'] = format_comments(item.get('discussion_and_comments', ''))

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Finished {file_path}.")

if __name__ == '__main__':
    process_file('qa_parsed.json')
    process_file('pde_parsed.json')
