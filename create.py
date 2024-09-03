import os
import shutil

# Define the updated folder structure
structure = {
    ".github": {},
    "configs": ["config.yaml", "logging.yaml"],
    "scripts": ["setup.sh", "deploy.sh"],
    "src": [
        "__init__.py",
        {
            "data_extraction": ["__init__.py", "extract_initial.py", "extract_refresh.py"]
        },
        {
            "embedding": ["__init__.py", "generate_embeddings_initial.py", "update_embeddings.py"]
        },
        {
            "inferencing": ["__init__.py", "inference_api.py", "query_processing.py", "reranking.py"]
        },
        "utils.py"
    ],
    "tests": ["__init__.py", "test_data_extraction.py", "test_embedding.py", "test_inferencing.py"],
    "app": ["__init__.py", "main.py", "model.py"]
}

def clear_and_create_directory(path):
    """Clear the directory if it exists, then create a new empty directory."""
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

def create_files_in_directory(directory_path, files):
    """Creates files and subdirectories within the given directory path."""
    for item in files:
        if isinstance(item, str):
            # If the item ends with '/', treat it as a directory
            if item.endswith('/'):
                os.makedirs(os.path.join(directory_path, item), exist_ok=True)
            else:
                file_path = os.path.join(directory_path, item)
                open(file_path, 'w').close()
        elif isinstance(item, dict):
            # Handle nested subfolders
            for subfolder, subfiles in item.items():
                subfolder_path = os.path.join(directory_path, subfolder)
                os.makedirs(subfolder_path, exist_ok=True)
                create_files_in_directory(subfolder_path, subfiles)

# Create the directories and files
def create_structure(base_path="."):
    for folder, files in structure.items():
        folder_path = os.path.join(base_path, folder)
        clear_and_create_directory(folder_path)
        create_files_in_directory(folder_path, files)

    # Create the Dockerfile in the root directory
    with open(os.path.join(base_path, "Dockerfile"), 'w') as f:
        f.write("""\
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""")

    # Create the requirements.txt file in the root directory
    with open(os.path.join(base_path, "requirements.txt"), 'w') as f:
        f.write("""\
fastapi
uvicorn
pydantic
qdrant-client
flake8
""")

    # Create the CI/CD workflow file in the root directory
    with open(os.path.join(base_path, "ci-cd.yml"), 'w') as f:
        f.write("""\
name: CI/CD Pipeline

on:
  push:
    tags:
      - 'v*.*.*-dev'
      - 'v*.*.*-test'
      - 'v*.*.*-stage'
      - 'v*.*.*-prod'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9

    - name: Install dependencies
      run: pip install -r requirements.txt

    - name: Linting
      run: flake8 app/

    - name: Build Docker image
      run: docker build -t llm-inference-pipeline:${{ github.ref_name }} .

    - name: Run Docker container
      run: docker run -d -p 8000:8000 llm-inference-pipeline:${{ github.ref_name }}

    - name: Run tests
      run: |
        curl -X POST "http://localhost:8000/infer" -H "Content-Type: application/json" -d '{"prompt": "Hello, LLM!"}'

    - name: Deploy to environment
      if: github.ref_name == 'v*.*.*-prod'
      run: echo "Deploying to production environment"
""")

if __name__ == "__main__":
    create_structure()
    print("Folder structure and files have been created.")

