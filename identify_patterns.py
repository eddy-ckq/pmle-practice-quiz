import json
import re

def get_option_pattern(options):
    if not options: return 'Unknown'
    
    is_step_based = False
    is_mapping = False
    is_code = False
    is_short = True
    
    for val in options.values():
        val = str(val).strip()
        if not val: continue
        
        # Check for sequential steps
        if re.search(r'(?:1\.\s.*?2\.\s|Step 1.*?Step 2|->|\bthen\b)', val, re.IGNORECASE):
            is_step_based = True
        
        # Check for mapping (e.g. 1 = Dataflow)
        if re.search(r'(?:\d\s*=\s*[A-Za-z]+|\b[A-Za-z]+\s*:\s*[A-Za-z]+)', val):
            is_mapping = True
            
        # Check for code or CLI commands
        if re.search(r'(?:SELECT .* FROM|CREATE TABLE|def \w+\(|import \w+|gcloud \w+)', val, re.IGNORECASE):
            is_code = True
            
        if len(val.split()) > 7:
            is_short = False

    if is_code: return 'Code/Command'
    if is_step_based: return 'Sequential Steps'
    if is_mapping: return 'Mapping/Association'
    if is_short: return 'Short Answer/Term'
    return 'Explanatory/Scenario'

def process_file(file_path, out_f):
    out_f.write(f'--- File: {file_path} ---\n')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for q in data:
            q_id = q.get('question_id', 'Unknown')
            ans = str(q.get('correct_answer', '')).strip()
            options = q.get('options', {})
            
            # Answer pattern
            ans_split = [x.strip() for x in ans.split(',')]
            if len(ans_split) > 1:
                ans_pattern = f'Multiple Choice ({len(ans_split)} answers)'
            else:
                ans_pattern = 'Single Choice'
                
            # Options format pattern
            opt_pattern = get_option_pattern(options)
            
            out_f.write(f'Question {q_id}:\n')
            out_f.write(f'  Answer Pattern: {ans_pattern}\n')
            out_f.write(f'  Options Pattern: {opt_pattern}\n')
        out_f.write('\n')
    except Exception as e:
        out_f.write(f'Error processing {file_path}: {e}\n\n')

if __name__ == '__main__':
    with open('output_patterns.txt', 'w', encoding='utf-8') as out_f:
        process_file('qa_parsed.json', out_f)
        process_file('pde_parsed.json', out_f)
    print("Successfully generated output_patterns.txt")
