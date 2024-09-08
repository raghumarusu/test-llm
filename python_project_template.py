import os
import shutil

def create_project_structure(base_name="fox_rag_template"):
    # Remove the existing folder if it exists
    if os.path.exists(base_name):
        shutil.rmtree(base_name)

    # Define the folder structure
    folders = [
        f"{base_name}/config",
        f"{base_name}/llm_pipeline",
        f"{base_name}/data_shared",
        f"{base_name}/logs"
    ]
    
    # Define files to be created
    files = {
        f"{base_name}/config/config.yml": "default_config_data",
        f"{base_name}/Dockerfile": "FROM python:3.9-slim\n# Dockerfile content here",
        f"{base_name}/.gitignore": "*.pyc\n__pycache__/\nenv/\n*.log",
        f"{base_name}/.env": "OPENAI_API_VERSION=\nAZURE_OPENAI_ENDPOINT=\nAZURE_OPENAI_API_KEY=",
        f"{base_name}/requirements.txt": "fastapi\ntransformers\ntorch\nuvicorn\nPyYAML",
        f"{base_name}/setup.py": setup_py_template(),
        f"{base_name}/llm_pipeline/__init__.py": "",
        f"{base_name}/llm_pipeline/intent_mapping.py": "def map_intent():\n    pass",
        f"{base_name}/llm_pipeline/search.py": "def search():\n    pass",
        f"{base_name}/llm_pipeline/semantic_search.py": "def semantic_search():\n    pass",
        f"{base_name}/llm_pipeline/reranker.py": "def reranker():\n    pass",
        f"{base_name}/llm_pipeline/llm_answer.py": "def llm_answer():\n    pass",
        f"{base_name}/llm_pipeline/utils.py": utils_py_template(),
        f"{base_name}/llm_pipeline/logging.py": logging_py_template(),
        f"{base_name}/fast_api.py": fastapi_py_template(),
    }

    # Create all directories
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    # Create all files with their content
    for file_path, file_content in files.items():
        with open(file_path, 'w') as file:
            file.write(file_content)

    print(f"Project structure for {base_name} has been created successfully.")


def setup_py_template():
    return """
from setuptools import setup, find_packages

setup(
    name='fox_rag_template',
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='RAG LLM Pipeline Project',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'fastapi',
        'uvicorn',
        'torch',
        'transformers',
        'PyYAML',
    ],
    python_requires='>=3.8',
)
"""

def utils_py_template():
    return """
import os
import yaml

def load_config(path="config/config.yml"):
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def set_api_environment_variables(config):
    os.environ["TOKENIZERS_PARALLELISM"] = config["gpt_api"]["tokenizers_parallelism"]
    os.environ["CUDA_VISIBLE_DEVICES"] = config["gpt_api"]["cuda_visible_devices"]
    os.environ['OPENAI_API_VERSION'] = os.getenv("OPENAI_API_VERSION")
    os.environ['AZURE_OPENAI_ENDPOINT'] = os.getenv("AZURE_OPENAI_ENDPOINT")
    os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
"""

def logging_py_template():
    return """
import logging

def setup_logging():
    logger = logging.getLogger("my-logger")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler('logs/app.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
"""

def fastapi_py_template():
    return """
from fastapi import FastAPI
from llm_pipeline import search, semantic_search, reranker, llm_answer

app = FastAPI()

@app.post("/search")
def search_endpoint(query: str):
    return search.search(query)

@app.post("/semantic_search")
def semantic_search_endpoint(query: str):
    return semantic_search.semantic_search(query)

@app.post("/rerank")
def rerank_endpoint(query: str):
    return reranker.reranker(query)

@app.post("/llm_answer")
def llm_answer_endpoint(query: str):
    return llm_answer.llm_answer(query)
"""

if __name__ == "__main__":
    create_project_structure()
