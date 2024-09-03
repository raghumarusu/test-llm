from fastapi import FastAPI
from app.model import infer

app = FastAPI()


@app.post("/infer")
def infer_llm(prompt: str):
    response = infer(prompt)
    return {"prompt": prompt, "response": response}
