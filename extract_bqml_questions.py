import json
import re

def filter_questions(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        questions = json.load(f)
        
    # Keywords related to the syllabus section
    keywords = [
        r'\bBigQuery ML\b', 
        r'\bBQML\b',
        r'\bBigQuery\b.*\bmodel\b',
        r'\bBigQuery\b.*\bpredict\b',
        r'\bBigQuery\b.*\bfeature engineering\b',
        r'\bBigQuery\b.*\bclassification\b',
        r'\bBigQuery\b.*\bregression\b',
        r'\bBigQuery\b.*\btime-series\b',
        r'\bBigQuery\b.*\bmatrix factorization\b',
        r'\bBigQuery\b.*\bboosted trees\b',
        r'\bBigQuery\b.*\bautoencoders\b'
    ]
    
    compiled_keywords = [re.compile(kw, re.IGNORECASE) for kw in keywords]
    
    matching_questions = []
    
    for q in questions:
        text_to_search = str(q.get('question_text', '')) + " " + " ".join(q.get('options', {}).values()) + " " + str(q.get('correct_answer', ''))
        
        # Check if any keyword matches
        if any(kw.search(text_to_search) for kw in compiled_keywords):
            matching_questions.append(q)
            
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Found " + str(len(matching_questions)) + " questions related to BigQuery ML." + chr(10) + chr(10))
        f.write("="*80 + chr(10) + chr(10))
        
        for q in matching_questions:
            f.write("Question #" + str(q['question_id']) + chr(10))
            f.write(str(q['question_text']) + chr(10) + chr(10))
            for key, val in q['options'].items():
                f.write(str(key) + ". " + str(val) + chr(10))
            f.write(chr(10) + "Correct Answer: " + str(q['correct_answer']) + chr(10))
            f.write("-" * 80 + chr(10) + chr(10))

if __name__ == "__main__":
    filter_questions('qa_parsed.json', 'bqml_questions.txt')
