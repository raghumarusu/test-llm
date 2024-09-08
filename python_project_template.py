import os

def create_project_structure(base_name="fox_rag_template"):
    # Define folder structure
    folders = [
        f"{base_name}/config",
        f"{base_name}/data_shared",
        f"{base_name}/llm_pipeline",
        f"{base_name}/logs"
    ]
    
    # Define files and their content
    files = {
        f"{base_name}/config/config.yml": """
gpt_api:
  version: "2024-09"
  api_endpoint: "https://api.openai.com/v1/"
  deployment: "production"
  tokenizers_parallelism: "true"
  cuda_visible_devices: "0"
        """,
        f"{base_name}/Dockerfile": """
# Dockerfile for fox_rag_template

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "fast_api:app", "--host", "0.0.0.0", "--port", "8000"]
        """,
        f"{base_name}/fast_api.py": """
from fastapi import FastAPI
from llm_pipeline.utils import load_config, set_api_environment_variables
from llm_pipeline.search import complete_search_with_id
from llm_pipeline.llm_answer import generate_answer_with_LLM_Intent

app = FastAPI()

# Load Config
config = load_config()

# Set Environment Variables
set_api_environment_variables(config)

@app.post("/")
async def predict(query: str, intent: str = None):
    # Perform search based on the query
    search_results = complete_search_with_id(query)
    
    # Generate final answer using the LLM based on reranked results
    final_answer = generate_answer_with_LLM_Intent(search_results)
    
    return {"answer": final_answer}
        """,
        f"{base_name}/.env": """
OPENAI_API_VERSION="v1"
AZURE_OPENAI_ENDPOINT="https://api.azure.com"
AZURE_OPENAI_API_KEY="your_api_key_here"
        """,
        f"{base_name}/.gitignore": """
# Python
*.pyc
__pycache__/

# Environment
.env

# Logs
/logs/

# Docker
docker-compose.yml
        """,
        f"{base_name}/llm_pipeline/__init__.py": "",
        f"{base_name}/llm_pipeline/embeddings.py": """
def define_embed_model():
    # Code to define and return embedding model
    pass

def read_in_vector_db():
    # Code to load vector database
    pass

def read_in_doc_store():
    # Code to load document store
    pass
        """,
        f"{base_name}/llm_pipeline/search.py": """
def complete_search_with_id(query_list, top_k=40, weight=0.6):
    # Code for complete search (vector and keyword-based)
    pass

def retrieve_documents_rag_fusion():
    # Code for RAG fusion
    pass
        """,
        f"{base_name}/llm_pipeline/reranker.py": """
def reranking(df_ss):
    # Code for reranking
    pass

def combine_child_parent(df):
    # Code to combine parent-child documents
    pass
        """,
        f"{base_name}/llm_pipeline/llm_answer.py": """
def generate_answer_with_LLM_Intent(df_reranked):
    # Code to generate an answer using the LLM
    pass
        """,
        f"{base_name}/llm_pipeline/logging.py": """
def search_logging(df_ss, transformed_queries, task, intent):
    # Code for logging search events
    pass

def reranker_logging(df_reranked):
    # Code for logging reranking events
    pass
        """,
        f"{base_name}/llm_pipeline/utils.py": """
import os
import yaml

def load_config(path="config/config.yml"):
    # Load configuration from YAML file
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def set_api_environment_variables(config):
    # Set environment variables for sensitive information
    os.environ["TOKENIZERS_PARALLELISM"] = config["gpt_api"]["tokenizers_parallelism"]
    os.environ["CUDA_VISIBLE_DEVICES"] = config["gpt_api"]["cuda_visible_devices"]
    os.environ['OPENAI_API_VERSION'] = os.getenv("OPENAI_API_VERSION")
    os.environ['AZURE_OPENAI_ENDPOINT'] = os.getenv("AZURE_OPENAI_ENDPOINT")
    os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
        """,
        f"{base_name}/logs/.gitkeep": "",
        f"{base_name}/requirements.txt": """
fastapi
uvicorn
openai
torch
PyYAML
        """,
        f"{base_name}/setup.py": """
from setuptools import setup, find_packages

setup(
    name="fox_rag_template",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
        'openai',
        'torch',
        'PyYAML'
    ],
)
        """
    }
    
    # Create directories
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    # Create files with content
    for file_path, content in files.items():
        with open(file_path, 'w') as file:
            file.write(content.strip())
    
    print(f"Project structure for {base_name} created successfully.")

# Run the function to create the project structure
create_project_structure()
