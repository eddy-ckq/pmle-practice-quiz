import json
import re

with open('correlations.json', 'r', encoding='utf-8') as f:
    correlations = json.load(f)

# More "active" reasoning templates
tech_reasoning = {
    "BIGQUERY": "BigQuery is selected here because the requirement involves large-scale analytics, SQL-based transformations, or structured data storage where a serverless data warehouse is the most efficient choice.",
    "VERTEX": "Vertex AI is the best fit because the goal is to manage the end-to-end ML lifecycle—including tracking, deployment, and monitoring—within a unified, production-ready platform.",
    "CLOUD STORAGE": "Cloud Storage is used here as a scalable data lake or durable object store, ideal for migrating Hadoop HDFS data or storing raw unstructured files at a low cost.",
    "DATAFLOW": "Dataflow is chosen because it provides a fully managed environment for Apache Beam pipelines, handling both streaming and batch data with automatic scaling and windowing support.",
    "PUB SUB": "Pub/Sub is the architectural choice for decoupling systems and ingesting high-volume event streams from diverse sources in real-time.",
    "AUTOML": "AutoML is the most efficient approach because it automates model creation and tuning, allowing high-quality models to be built with minimal manual coding or ML expertise.",
    "DATAPROC": "Dataproc is used to directly migrate and run existing Apache Spark or Hadoop clusters on GCP with minimal changes to your existing scripts.",
    "GPU": "GPUs are required here to provide the hardware acceleration necessary for deep learning tasks and training large custom models like TensorFlow or PyTorch.",
    "BIGTABLE": "Bigtable is selected for its ability to handle massive NoSQL workloads with extremely high throughput and low latency, specifically for time-series or analytical data.",
    "COMPOSER": "Cloud Composer (managed Airflow) is used to orchestrate complex workflows and schedule dependencies across multiple GCP services in a reliable way.",
    "CLOUD SQL": "Cloud SQL provides a fully managed relational database, handling maintenance and backups for your MySQL or PostgreSQL workloads while maintaining standard SQL compatibility.",
    "KUBEFLOW": "Kubeflow is used to deploy and manage portable, scalable ML workflows on Kubernetes, providing a robust open-source foundation for complex ML pipelines.",
    "DATAPREP": "Dataprep is the choice for visually exploring and cleaning data, allowing non-developers to prepare datasets for analysis without writing transformation code.",
    "DATAPLEX": "Dataplex is used to manage and govern data across a distributed 'data mesh', providing central monitoring and security for data across lakes and warehouses."
}

stopwords = set("i me my myself we our ours ourselves you your yours yourself yourselves he him his himself she her hers herself it its itself they them their theirs themselves what which who whom this that these those am is are was were be been being have has had having do does did doing a an the and but if or because as until while of at by for with about against between into through during before after above below to from up down in out on off over under again further then once here there when where why how all any both each few more most other some such no nor not only own same so than too very s t can will just don should now want use need needs using would could like best most least true false correct incorrect".split())

def normalize(text):
    return re.sub(r'[^a-zA-Z0-9\s]', ' ', str(text).lower())

def extract_community_reasoning(discussion, correct_answers):
    if not discussion:
        return ""
    
    ans_list = [a.strip() for a in correct_answers.split(',')]
    lines = [line.strip() for line in discussion.split('\n') if line.strip()]
    
    # Try to find the "best" explanation (longer sentences usually contain more reasoning)
    best_line = ""
    for ans in ans_list:
        # Priority 1: Lines mentioning the answer letter AND having meaningful length
        for line in lines:
            if re.search(r'\b' + ans + r'\b', line, re.IGNORECASE) and len(line.split()) > 12:
                clean_line = re.sub(r'^-?\s*(?:Selected Answer:\s*[A-Z, ]+)?\s*', '', line, flags=re.IGNORECASE)
                if len(clean_line) > len(best_line):
                    best_line = clean_line

    if best_line: return best_line

    # Priority 2: Any long sentence
    for line in lines:
        clean_line = re.sub(r'^-?\s*(?:Selected Answer:\s*[A-Z, ]+)?\s*', '', line, flags=re.IGNORECASE)
        if len(clean_line.split()) > 15:
            return clean_line
            
    return ""

def generate_explanation(q_text, correct_answer_text, correct_letter, discussion):
    """
    Generates a technical explanation by prioritizing architectural patterns over simple keywords.
    """
    q_lower = q_text.lower()
    c_lower = correct_answer_text.lower()
    
    community_insight = extract_community_reasoning(discussion, correct_letter)
    community_html = f"<br><br><strong>Key Community Insight:</strong> <em>\"{community_insight}\"</em>" if community_insight else ""
    
    # 1. Primary Strategy: Match architectural keywords from the question to a technology in the answer.
    # This is the most reliable way to generate a high-quality explanation.
    for tech, data in correlations.items():
        # Check if the technology (e.g., "BigQuery", "Vertex AI") is mentioned in the correct answer text.
        tech_variants = [tech.lower(), tech.replace(' ', '').lower()]
        found_tech_in_answer = any(tv in c_lower for tv in tech_variants)
        
        if found_tech_in_answer:
            # Now, check if any of the associated keywords (e.g., "serverless", "end-to-end ML") are in the question.
            for kw_obj in data['keywords']:
                kw = kw_obj['keyword'].lower()
                if f'"{kw}"' in q_lower or f" {kw} " in q_lower:
                    reason = tech_reasoning.get(tech, data['explanation'])
                    # This creates a strong, direct link: Question asks for X, Answer provides Y, which is the GCP tool for X.
                    return (f"💡 <b>Architectural Fit:</b> The question highlights a need for <b>`{kw}`</b>. "
                            f"The correct answer proposes using <b>{tech}</b>, which is Google Cloud's primary service for this exact purpose. "
                            f"{reason}{community_html}")

    # 2. Fallback Strategy: If no direct architectural link is found, rely on the community insight.
    # This is often more valuable than a weakly-guessed AI explanation.
    if community_insight:
        return (f"💡 <b>Community-Driven Answer:</b> While a direct keyword match wasn't found, the community discussion provides the clearest reasoning for selecting this answer. "
                f"It follows established Google Cloud best practices for the scenario described.{community_html}")
        
    # 3. Final Fallback: A generic but safe explanation if no other signals are found.
    return ("💡 <b>General Best Practice:</b> This solution represents the most direct and effective architectural approach "
            "for the requirements outlined in the question, adhering to Google Cloud's recommended best practices.")

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
    print("Successfully improved AI explanations.")
