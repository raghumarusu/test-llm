import os
import shutil

# Define the updated folder structure
structure = {
    ".github": {},  # Create an empty .github folder
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
        "utils.py",
    ],
    "tests": ["__init__.py", "test_data_extraction.py", "test_embedding.py", "test_inferencing.py"],
    "app": [
        "__init__.py",
        "main.py",
        "model.py"
    ],
    "docker": ["Dockerfile"],
    "requirements.txt": None,
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
            file_path = os.path.join(directory_path, item)
            if os.path.exists(file_path):
                os.remove(file_path)
            open(file_path, 'w').close()
        elif isinstance(item, dict):
            # Handle nested subfolders
            for subfolder, subfiles in item.items():
                subfolder_path = os.path.join(directory_path, subfolder)
                if os.path.exists(subfolder_path):
                    shutil.rmtree(subfolder_path)
                os.makedirs(subfolder_path, exist_ok=True)
                create_files_in_directory(subfolder_path, subfiles)

def populate_files(base_path="."):
    # Write the content for `main.py`
    with open(os.path.join(base_path, "app/main.py"), 'w') as f:
        f.write("""from fastapi import FastAPI
from app.model import infer

app = FastAPI()

@app.post("/infer")
def infer_llm(prompt: str):
    response = infer(prompt)
    return {"prompt": prompt, "response": response}
""")

    # Write the content for `model.py`
    with open(os.path.join(base_path, "app/model.py"), 'w') as f:
        f.write("""def infer(prompt: str) -> str:
    # Simulate LLM response
    return f"Simulated LLM response to: {prompt}"
""")

    # Write the content for `Dockerfile`
    with open(os.path.join(base_path, "docker/Dockerfile"), 'w') as f:
        f.write("""# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""")

    # Write the content for `requirements.txt`
    with open(os.path.join(base_path, "requirements.txt"), 'w') as f:
        f.write("fastapi\nuvicorn\n")

    # Write the content for `ci-cd.yml` in the root directory
    with open(os.path.join(base_path, "ci-cd.yml"), 'w') as f:
        f.write("""name: CI/CD Pipeline

on:
  push:
    tags:
      - 'v*.*.*-dev'
      - 'v*.*.*-test'
      - 'v*.*.*-stage'
      - 'v*.*.*-prod'

jobs:
  build:
    runs-on: ubuntu-latest  # Can be set to macos-latest if needed

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

    - name: Stop any running container on port 8000
      run: |
        existing_container=$(docker ps -q --filter "publish=8000")
        if [ -n "$existing_container" ]; then
          echo "Stopping container running on port 8000..."
          docker stop $existing_container
          docker rm $existing_container
        fi

    - name: Build Docker image
      run: docker build -t llm-inference-pipeline:${{ github.ref_name }} .

    - name: Run Docker container
      run: docker run -d --name llm_container -p 8000:8000 llm-inference-pipeline:${{ github.ref_name }}

    - name: Wait for the service to start
      run: sleep 20  # Increased sleep time to 20 seconds

    - name: Test API endpoint
      run: |
        curl -X POST "http://localhost:8000/infer" -H "Content-Type: application/json" -d '{"prompt": "Hello, LLM!"}'

    - name: Check Docker container logs if curl fails
      if: failure()
      run: docker logs llm_container

    - name: Stop and remove Docker container
      run: |
        docker stop llm_container
        docker rm llm_container

    - name: Deploy to environment
      if: github.ref_name == 'v*.*.*-prod'
      run: echo "Deploying to production environment"

    # Lab server deployment

    # The following steps build and save the Docker image directly on a remote server
    # - name: Build Docker image on remote server
    #   run: |
    #     ssh user@remote_server "
    #       cd /path/to/project &&
    #       docker build -t llm-inference-pipeline:${{ github.ref_name }} . &&
    #       docker save -o /path/to/save/location/llm-inference-pipeline-${{ github.ref_name }}.tar llm-inference-pipeline:${{ github.ref_name }}"
    #     echo "Docker image built and saved on remote server."

    # - name: Deploy Docker image on remote server
    #   run: |
    #     ssh user@remote_server "
    #       docker load -i /path/to/save/location/llm-inference-pipeline-${{ github.ref_name }}.tar &&
    #       docker run -d --name llm_container -p 8000:8000 llm-inference-pipeline:${{ github.ref_name }}"
    #     echo "Application deployed on remote server."


	# AWS Deployment

    # The following steps build and save the Docker image directly on an AWS EC2 instance .

    # - name: Build Docker image on AWS EC2
    #   run: |
    #     ssh -i /path/to/your/aws-ec2-key.pem ec2-user@your-ec2-public-ip "
    #       cd /path/to/project &&
    #       docker build -t llm-inference-pipeline:${{ github.ref_name }} . &&
    #       docker save -o /path/to/save/location/llm-inference-pipeline-${{ github.ref_name }}.tar llm-inference-pipeline:${{ github.ref_name }}"
    #     echo "Docker image built and saved on AWS EC2 instance."

    # - name: Deploy Docker image on AWS EC2
    #   run: |
    #     ssh -i /path/to/your/aws-ec2-key.pem ec2-user@your-ec2-public-ip "
    #       docker load -i /path/to/save/location/llm-inference-pipeline-${{ github.ref_name }}.tar &&
    #       docker run -d --name llm_container -p 8000:8000 llm-inference-pipeline:${{ github.ref_name }}"
    #     echo "Application deployed on AWS EC2 instance."

""")

# Create the directories and files
def create_structure(base_path="."):
    for folder, files in structure.items():
        folder_path = os.path.join(base_path, folder)
        if files is None:
            # Handle the special case for `requirements.txt`
            file_path = os.path.join(base_path, folder)
            if os.path.exists(file_path):
                os.remove(file_path)
            open(file_path, 'w').close()
        else:
            clear_and_create_directory(folder_path)
            create_files_in_directory(folder_path, files)

    populate_files(base_path)
    print("Folder structure and files have been created.")

if __name__ == "__main__":
    create_structure()

