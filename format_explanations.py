import json
import re
import argparse
import os

def markdown_to_html(text):
    """
    Converts basic Markdown syntax (###, **) to corresponding HTML tags.
    """
    if not isinstance(text, str):
        return text

    # Handle ### headers
    text = re.sub(r'^###\s*(.*)', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    
    # Handle **bold** text
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Handle numbered lists (e.g., 1. item)
    # This is a bit more complex to handle correctly with just regex.
    # We will find all list-like lines and wrap them.
    lines = text.split('\n')
    in_list = False
    new_lines = []
    for line in lines:
        match = re.match(r'^\s*\d+\.\s*(.*)', line)
        if match:
            if not in_list:
                in_list = True
                new_lines.append('<ul style="list-style-type: decimal; margin-left: 20px;">')
            new_lines.append(f'<li>{match.group(1)}</li>')
        else:
            if in_list:
                in_list = False
                new_lines.append('</ul>')
            new_lines.append(line)
    
    if in_list:
        new_lines.append('</ul>')

    text = '\n'.join(new_lines)

    # Convert remaining newlines to <br> for proper HTML display
    text = text.replace('\n', '<br>')
    
    return text

def process_file(file_path):
    """
    Reads a JSON file, formats the ai_explanation field from Markdown to HTML,
    and overwrites the file with the formatted content.
    """
    print(f"--- Formatting explanations in {file_path} ---")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing {file_path}: {e}")
        return

    questions_changed = 0
    for q in data:
        explanation = q.get('ai_explanation')
        if explanation and '###' in explanation: # Only process if it looks like Markdown
            parts = explanation.split('\n', 1)
            header = parts[0]
            markdown_content = parts[1] if len(parts) > 1 else ''
            
            html_content = markdown_to_html(markdown_content)
            q['ai_explanation'] = header + "<br>" + html_content
            questions_changed += 1

    if questions_changed > 0:
        print(f"  Found and converted explanations for {questions_changed} questions.")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"  Successfully saved formatted explanations to {file_path}")
    else:
        print("  No Markdown explanations found that needed formatting.")

    print(f"--- Finished processing {file_path} ---")

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown in AI explanations to HTML.")
    parser.add_argument('file', help='The JSON file to process (e.g., qa_parsed.json).')
    
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found at '{args.file}'")
        return
        
    process_file(args.file)

if __name__ == '__main__':
    main()
