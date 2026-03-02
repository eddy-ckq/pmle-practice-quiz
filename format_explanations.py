import json
import argparse
import os
import markdown
import re

def convert_explanation_to_html(explanation_text):
    """
    Takes the raw explanation text, preserves the custom header,
    and converts the body from Markdown to HTML using a robust two-pass method.
    """
    if not isinstance(explanation_text, str):
        return explanation_text

    # Check if formatting is likely needed
    if '###' not in explanation_text and '**' not in explanation_text:
        return explanation_text

    # 1. Split the custom header from the markdown body
    parts = explanation_text.split('\n', 1)
    header = parts[0]
    markdown_body = parts[1] if len(parts) > 1 else ''

    # 2. First Pass: Use the markdown library for primary conversion
    # This correctly handles headers, lists, etc.
    html_body = markdown.markdown(markdown_body)

    # 3. Second Pass: Use a targeted regex to forcefully convert any remaining **bold** tags
    # that the library might have missed. This is a common issue with nested or
    # oddly-spaced markdown.
    html_body = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_body)
    
    # 4. Reassemble
    return header + "<br>" + html_body

def process_file(file_path):
    """
    Reads a JSON file, formats the ai_explanation field,
    and overwrites the file with the formatted content.
    """
    print(f"--- Running 2-Pass Formatting on {file_path} ---")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing {file_path}: {e}")
        return

    questions_changed = 0
    for q in data:
        original_explanation = q.get('ai_explanation')
        if original_explanation:
            formatted_explanation = convert_explanation_to_html(original_explanation)
            if original_explanation != formatted_explanation:
                q['ai_explanation'] = formatted_explanation
                questions_changed += 1

    if questions_changed > 0:
        print(f"  Found and correctly formatted explanations for {questions_changed} questions.")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"  Successfully saved final formatting to {file_path}")
    else:
        print("  No explanations needed additional formatting.")

    print(f"--- Finished processing {file_path} ---")

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown in AI explanations to HTML using a robust two-pass method.")
    parser.add_argument('file', help='The JSON file to process (e.g., qa_parsed.json).')
    
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found at '{args.file}'")
        return
        
    process_file(args.file)

if __name__ == '__main__':
    main()
