from fastapi import FastAPI
from pydantic import BaseModel
from nlp_processor import process_sentence_for_i3rab

app = FastAPI()

class SentenceRequest(BaseModel):
    text: str

@app.post("/analyze")
def analyze_sentence(request: SentenceRequest):
    result = process_sentence_for_i3rab(request.text)
    return {"analysis": result}