import json
import re

explanations = {
    'BIGQUERY': 'BigQuery is Google Cloud\'s fully managed, serverless, highly scalable data warehouse. It is ideal for analyzing massive datasets (millions of records), structured data, and performing analytics.',
    'VERTEX': 'Vertex AI is Google Cloud\'s unified ML platform. It handles the entire ML lifecycle including model training, serving, deployment, and tracking lineage/artifacts to productionize ML pipelines.',
    'CLOUD STORAGE': 'Cloud Storage is an object storage service often used as a data lake, a target for on-premises Hadoop/HDFS migrations, and for storing unstructured files or disaster recovery (RPO).',
    'DATAFLOW': 'Dataflow is a fully managed streaming and batch data processing service. It is highly associated with building data pipelines to ingest and process high volumes of data globally.',
    'PUB SUB': 'Pub/Sub is a messaging service for decoupling systems. It is commonly used for ingesting event streams from devices, application servers, or tracking shipments in logistics.',
    'AUTOML': 'AutoML allows users to train high-quality machine learning models with minimal effort, often without writing any code, automating feature selection and hyperparameter tuning.',
    'DATAPROC': 'Dataproc is a managed Spark and Hadoop service. It is the direct answer for migrating on-premises Apache Spark, PySpark, Hive, and Hadoop clusters to Google Cloud.',
    'AI PLATFORM': 'AI Platform is the legacy suite (now Vertex AI) for training and deploying ML models, sometimes featured in older exam questions relating to advertising or generic model deployments.',
    'GPU': 'GPUs (like NVIDIA) provide the necessary hardware acceleration for training deep learning and custom TensorFlow/PyTorch models efficiently.',
    'BIGTABLE': 'Cloud Bigtable is a fully managed, scalable NoSQL database service for large analytical and operational workloads, particularly excelling at high-throughput time-series data.',
    'COMPOSER': 'Cloud Composer is a fully managed workflow orchestration service built on Apache Airflow. It is the go-to tool for scheduling and managing complex pipelines.',
    'CLOUD SQL': 'Cloud SQL is a fully managed relational database service for MySQL, PostgreSQL, and SQL Server.',
    'KUBEFLOW': 'Kubeflow is an open-source ML platform dedicated to making deployments of ML workflows on Kubernetes simple, portable and scalable, providing end-to-end architectures.',
    'DATAPREP': 'Dataprep by Trifacta is an intelligent data service for visually exploring, cleaning, and preparing data for analysis and machine learning.',
    'DATAPLEX': 'Dataplex is an intelligent data fabric that enables organizations to centrally discover, manage, monitor, and govern their data across data lakes, data warehouses, and data marts, often associated with a \'data mesh\' architecture.'
}

def parse_txt_to_json():
    with open('correlations.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        
    blocks = re.split(r'^=== (.*?) ===', content, flags=re.MULTILINE)
    
    correlations_data = {}
    
    for i in range(1, len(blocks), 2):
        tech_name = blocks[i].strip()
        body = blocks[i+1]
        
        keywords_match = re.findall(r"-\s+'(.*?)':\s+(\d+)%.*?\(In (\d+) out of (\d+)", body)
        
        tech_data = {
            'tech': tech_name,
            'explanation': explanations.get(tech_name, tech_name + ' is commonly used for this pattern in Google Cloud.'),
            'keywords': []
        }
        
        for kw, pct, count, total in keywords_match:
            tech_data['keywords'].append({
                'keyword': kw,
                'percentage': int(pct),
                'count': int(count),
                'total': int(total)
            })
            
        correlations_data[tech_name] = tech_data
        
    with open('correlations.json', 'w', encoding='utf-8') as f:
        json.dump(correlations_data, f, indent=2)
        
if __name__ == '__main__':
    parse_txt_to_json()