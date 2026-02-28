import json
import re
from collections import defaultdict, Counter

def normalize(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', str(text).lower())
    return text

def run_analysis():
    files = ['qa_parsed.json', 'pde_parsed.json']
    
    q_words_cnt = Counter()
    a_words_cnt = Counter()
    co_occur = defaultdict(Counter)
    
    stopwords = set("i me my myself we our ours ourselves you your yours yourself yourselves he him his himself she her hers herself it its itself they them their theirs themselves what which who whom this that these those am is are was were be been being have has had having do does did doing a an the and but if or because as until while of at by for with about against between into through during before after above below to from up down in out on off over under again further then once here there when where why how all any both each few more most other some such no nor not only own same so than too very s t can will just don should now want use need needs using would could like best most least true false correct incorrect".split())

    def get_terms(text):
        terms = set()
        words = [w for w in normalize(text).split() if w not in stopwords and len(w)>2]
        terms.update(words)
        # add bigrams
        for i in range(len(words)-1):
            terms.add(words[i] + ' ' + words[i+1])
        return terms

    target_techs = {
        'bigquery', 'dataflow', 'dataproc', 'pub sub', 'pubsub', 'cloud storage', 
        'vertex', 'automl', 'kubeflow', 'ai platform', 'bigtable', 'spanner', 
        'cloud sql', 'firestore', 'datastore', 'dataprep', 'data fusion', 
        'composer', 'looker', 'data studio', 'tensorflow', 'pytorch', 'scikit', 
        'xgboost', 'keras', 'kmeans', 'k means', 'logistic regression', 
        'linear regression', 'arima', 'pca', 'cnn', 'rnn', 'lstm', 'bert', 
        'tpu', 'gpu', 'cloud functions', 'cloud run', 'app engine', 'kubernetes', 'gke', 'dataplex'
    }

    for file in files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            continue
            
        for q in data:
            q_text = q.get('question_text', '')
            q_terms = get_terms(q_text)
            
            ans_letters = [a.strip() for a in str(q.get('correct_answer', '')).split(',') if a.strip()]
            options = q.get('options', {})
            a_text = " ".join([str(options.get(let, "")) for let in ans_letters])
            a_terms = get_terms(a_text)
            
            found_techs = set()
            for t in target_techs:
                if t in normalize(a_text):
                    found_techs.add(t)
            
            for qt in q_terms:
                q_words_cnt[qt] += 1
                for ft in found_techs:
                    co_occur[ft][qt] += 1
            
            for ft in found_techs:
                a_words_cnt[ft] += 1
                
    with open('correlations.txt', 'w', encoding='utf-8') as f:
        f.write("--- Question Keywords -> Correct Answer Tech/Service Correlations ---\n\n")
        f.write("This shows how specific words/phrases in a question strongly correlate with a specific technology/service being the correct answer.\n\n")
        
        sorted_techs = sorted(a_words_cnt.items(), key=lambda x: x[1], reverse=True)
        
        for tech, total_count in sorted_techs:
            if total_count < 3: continue
            
            best = []
            for qt, count in co_occur[tech].items():
                prob = count / q_words_cnt[qt]
                if count >= 3 and q_words_cnt[qt] >= 3 and prob >= 0.4:
                    if qt == tech or qt in tech or tech in qt:
                        continue
                    best.append((qt, count, prob, q_words_cnt[qt]))
            
            if best:
                best.sort(key=lambda x: (x[2], x[1]), reverse=True)
                
                f.write(f"=== {tech.upper()} === (Correct answer in {total_count} questions)\n")
                f.write("Strongly correlated question keywords:\n")
                for qt, c, prob, total_qt in best[:15]:
                    f.write(f"  - '{qt}': {prob*100:.0f}% correlation (In {c} out of {total_qt} questions with this keyword)\n")
                f.write("\n")

if __name__ == '__main__':
    run_analysis()