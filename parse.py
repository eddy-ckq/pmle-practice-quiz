import re
import json

def parse_dump(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Clean up page headers/footers
    text = re.sub(r'https://shop542998714.*?https://www\.goofish\.com.*?' + chr(10), '', text)
    text = re.sub(r'Exam Professional Machine Learning Engineer.*?' + chr(10), '', text)
    text = re.sub(r'淘宝:.*?' + chr(10), '', text)
    text = re.sub(r'咸鱼:.*?' + chr(10), '', text)
    text = re.sub(r'微信:.*?' + chr(10), '', text)
    
    # Split by Question #
    parts = re.split(r'(Question #\d+)', text)
    
    questions = []
    
    for i in range(1, len(parts), 2):
        try:
            q_id_match = re.search(r'\d+', parts[i])
            q_id = q_id_match.group(0) if q_id_match else "unknown"
            
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
                
            core_block = block[:split_idx]
            comments = block[split_idx:].strip()
                
            options = {}
            lines = core_block.split(chr(10))
            question_text_lines = []
            current_opt = None
            
            for line in lines:
                line_stripped = line.strip()
                opt_match = re.match(r'^([A-F])[\.\)]\s*(.*)', line_stripped)
                if opt_match:
                    current_opt = opt_match.group(1)
                    options[current_opt] = opt_match.group(2) + chr(10)
                elif current_opt:
                    options[current_opt] += line + chr(10)
                else:
                    question_text_lines.append(line)
            
            question_text = chr(10).join(question_text_lines).strip()
            
            for k in options:
                opt_text = options[k].strip()
                # Remove 'Most Voted' at the end of the option text
                opt_text = re.sub(r'\s*Most Voted$', '', opt_text, flags=re.IGNORECASE)
                options[k] = opt_text
                
            questions.append({
                "question_id": q_id,
                "question_text": question_text,
                "options": options,
                "correct_answer": correct_answer,
                "discussion_and_comments": comments[:1000] + ("..." if len(comments) > 1000 else "")
            })
        except Exception as e:
            print(f"Error parsing question {i}: {e}")
            continue
            
    return questions

if __name__ == "__main__":
    qs = parse_dump("extracted.txt")
    with open("qa_parsed.json", "w", encoding="utf-8") as f:
        json.dump(qs, f, indent=2, ensure_ascii=False)
