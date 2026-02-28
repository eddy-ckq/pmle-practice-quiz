import json
import re

with open('correlations.json', 'r', encoding='utf-8') as f:
    correlations = json.load(f)

stopwords = set("i me my myself we our ours ourselves you your yours yourself yourselves he him his himself she her hers herself it its itself they them their theirs themselves what which who whom this that these those am is are was were be been being have has had having do does did doing a an the and but if or because as until while of at by for with about against between into through during before after above below to from up down in out on off over under again further then once here there when where why how all any both each few more most other some such no nor not only own same so than too very s t can will just don should now want use need needs using would could like best most least true false correct incorrect".split())

def normalize(text):
    return re.sub(r'[^a-zA-Z0-9\s]', ' ', str(text).lower())

def get_snippet(text, word):
    word_escaped = re.escape(word)
    match = re.search(r'(.{0,40}\b' + word_escaped + r'\b.{0,40})', text, re.IGNORECASE)
    if match:
        return "..." + match.group(1).strip() + "..."
    return word

def extract_community_reasoning(discussion, correct_answers):
    if not discussion:
        return ""
    
    ans_list = [a.strip() for a in correct_answers.split(',')]
    lines = [line.strip() for line in discussion.split('\n') if line.strip()]
    
    # 1. Look for lines that explicitly mention "Answer is X", "Option X", or "X is correct"
    for ans in ans_list:
        pattern = r'(?i)(answer is\s*' + ans + r'|option\s*' + ans + r'|\b' + ans + r'\s*is correct|correct answer is\s*' + ans + r')'
        for line in lines:
            if re.search(pattern, line) and len(line.split()) > 7:
                clean_line = re.sub(r'^-?\s*(?:Selected Answer:\s*[A-Z, ]+)?\s*', '', line, flags=re.IGNORECASE)
                return clean_line

    # 2. Look for lines that mention the letter
    for ans in ans_list:
        pattern = r'\b' + ans + r'\b'
        for line in lines:
            if re.search(pattern, line) and len(line.split()) > 7:
                clean_line = re.sub(r'^-?\s*(?:Selected Answer:\s*[A-Z, ]+)?\s*', '', line, flags=re.IGNORECASE)
                return clean_line
                
    # 3. Fallback to the first line that looks like a reasonable sentence
    for line in lines:
        clean_line = re.sub(r'^-?\s*(?:Selected Answer:\s*[A-Z, ]+)?\s*', '', line, flags=re.IGNORECASE)
        if len(clean_line.split()) > 10:
            return clean_line
            
    return ""

def generate_explanation(q_text, correct_answer_text, correct_letter, discussion):
    q_lower = q_text.lower()
    c_lower = correct_answer_text.lower()
    
    community_insight = extract_community_reasoning(discussion, correct_letter)
    community_html = f"<br><br><strong>Community Insight:</strong> <em>\"{community_insight}\"</em>" if community_insight else ""
    
    for tech, data in correlations.items():
        tech_variants = [tech, tech.replace(' ', ''), tech.replace(' ', '/')]
        found_tech_str = None
        for tv in tech_variants:
            if tv.lower() in c_lower:
                found_tech_str = tv
                break
                
        if found_tech_str:
            for kw in data['keywords']:
                if kw['keyword'].lower() in q_lower:
                    ans_snippet = get_snippet(correct_answer_text, found_tech_str)
                    return f'💡 <b>AI Explanation:</b> The question highlights the phrase <b>"{kw["keyword"]}"</b>, which has a {kw["percentage"]}% correlation with <b>{tech}</b>. The correct answer maps to this via <b>"{ans_snippet}"</b>.' + community_html + f'<br><br><em>{data["explanation"]}</em>'
                    
    # fallback to word overlap
    q_words = [w for w in normalize(q_text).split() if w not in stopwords and len(w) > 4]
    c_words = [w for w in normalize(correct_answer_text).split() if w not in stopwords and len(w) > 4]
    
    overlap = set(q_words).intersection(set(c_words))
    if overlap:
        best_words = list(overlap)[:2]
        kw_str = '", "'.join(best_words)
        return f'💡 <b>AI Explanation:</b> The question emphasizes <b>"{kw_str}"</b>, which directly maps to the keyword(s) <b>"{kw_str}"</b> found in the correct answer. This alignment indicates it is the correct architectural choice.' + community_html
        
    return '💡 <b>AI Explanation:</b> The correct answer accurately addresses the specific constraints and objectives described in the question.' + community_html

def process(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for q in data:
        ans_letters = [a.strip() for a in q.get('correct_answer', '').split(',')]
        c_text = " ".join([str(q.get('options', {}).get(l, "")) for l in ans_letters])
        
        q['ai_explanation'] = generate_explanation(
            q.get('question_text', ''), 
            c_text, 
            q.get('correct_answer', ''), 
            q.get('discussion_and_comments', '')
        )
        
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    process('qa_parsed.json')
    process('pde_parsed.json')
    print("Successfully generated AI explanations for all questions.")
