import re
import json
import sys

def parse_dump(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Clean up page headers/footers
    text = re.sub(r'https://shop542998714.*?https://www\.goofish\.com.*?\n', '', text)
    text = re.sub(r'Exam Professional Data Engineer All Actual Questions.*?\n', '', text)
    text = re.sub(r'淘宝:.*?\n', '', text)
    text = re.sub(r'咸鱼:.*?\n', '', text)
    text = re.sub(r'微信:.*?\n', '', text)
    text = re.sub(r'(?m)^Topic \d+\n', '', text)
    
    # Split by Question # at the start of a line to avoid matching in-text references
    parts = re.split(r'(?m)^Question #(\d+)', text)
    
    # parts[0] is everything before the first question
    # parts[1] is '1', parts[2] is the block for Q1, parts[3] is '2', etc.
    
    questions = []
    
    for i in range(1, len(parts), 2):
        try:
            q_id = parts[i]
            block = parts[i+1].strip()
            
            # Find Correct Answer:
            correct_ans_match = re.search(r'Correct Answer:\s*([A-Z,]+)', block)
            correct_answer = correct_ans_match.group(1) if correct_ans_match else ""
            
            # Find Comments
            comments_match = re.search(r'\nComments\n', block)
            
            split_idx = len(block)
            if correct_ans_match and comments_match:
                split_idx = min(correct_ans_match.start(), comments_match.start())
            elif correct_ans_match:
                split_idx = correct_ans_match.start()
            elif comments_match:
                split_idx = comments_match.start()
                
            core_block = block[:split_idx].strip()
            comments = block[split_idx:].strip() if split_idx < len(block) else ""
            
            # We need to find options A, B, C, D...
            # The options block usually starts at the first occurrence of "\nA. " or "\nA) "
            options_start_match = re.search(r'(?:^|\n)([A-F])[\.\)]\s+', core_block)
            
            if options_start_match:
                question_text_part = core_block[:options_start_match.start()].strip()
                options_part = core_block[options_start_match.start():].strip()
            else:
                question_text_part = core_block
                options_part = ""
            
            # Check for case study in question_text_part
            case_study_title = ""
            cs_match = re.search(r'(.*?Case Study -)', question_text_part)
            if cs_match:
                case_study_title = cs_match.group(1).strip()
            
            options = {}
            if options_part:
                # Split options part by option letters
                opt_matches = list(re.finditer(r'(?:^|\n)([A-F])[\.\)]\s+', options_part))
                for j in range(len(opt_matches)):
                    start = opt_matches[j].end()
                    end = opt_matches[j+1].start() if j+1 < len(opt_matches) else len(options_part)
                    opt_letter = opt_matches[j].group(1)
                    opt_text = options_part[start:end].strip()
                    opt_text = re.sub(r'\s*Most Voted$', '', opt_text, flags=re.IGNORECASE)
                    options[opt_letter] = opt_text
            
            questions.append({
                "question_id": q_id,
                "case_study": case_study_title,
                "question_text": question_text_part,
                "options": options,
                "correct_answer": correct_answer,
                "discussion_and_comments": comments[:1500] + ("..." if len(comments) > 1500 else "")
            })
        except Exception as e:
            print(f"Error parsing question {i}: {e}")
            continue
            
    return questions

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python parse_pde.py <input.txt> <output.json>")
        sys.exit(1)
    qs = parse_dump(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(qs, f, indent=2, ensure_ascii=False)
