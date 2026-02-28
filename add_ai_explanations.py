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

def generate_explanation(q_text, correct_answer_text):
    q_lower = q_text.lower()
    c_lower = correct_answer_text.lower()
    
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
                    return f'💡 **AI Explanation:** The question highlights the phrase **"{kw["keyword"]}"**, which has a {kw["percentage"]}% correlation with **{tech}**. The correct answer maps to this via **"{ans_snippet}"**. <br><br><em>{data["explanation"]}</em>'
                    
    # fallback to word overlap
    q_words = [w for w in normalize(q_text).split() if w not in stopwords and len(w) > 4]
    c_words = [w for w in normalize(correct_answer_text).split() if w not in stopwords and len(w) > 4]
    
    overlap = set(q_words).intersection(set(c_words))
    if overlap:
        best_words = list(overlap)[:2]
        kw_str = '", "'.join(best_words)
        return f'💡 **AI Explanation:** The question emphasizes **"{kw_str}"**, which directly maps to the keyword(s) **"{kw_str}"** found in the correct answer. This alignment indicates it is the correct architectural choice.'
        
    return '💡 **AI Explanation:** The correct answer accurately addresses the specific constraints and objectives described in the question.'

def process(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for q in data:
        ans_letters = [a.strip() for a in q.get('correct_answer', '').split(',')]
        c_text = " ".join([str(q.get('options', {}).get(l, "")) for l in ans_letters])
        
        q['ai_explanation'] = generate_explanation(q.get('question_text', ''), c_text)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

process('qa_parsed.json')
process('pde_parsed.json')
print("Successfully generated AI explanations for all questions.")
