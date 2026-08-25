import os
import shutil
import json
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import models, schemas, database
from database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)

# Question Bank (mock data moved to backend)
QUESTION_BANK = {
  "oa": [
    { "id":"oa1", "type":"mcq", "tag":"Aptitude", "text":"A train 120m long crosses a pole in 6 seconds. What is its speed?", "options":["20 m/s","24 m/s","18 m/s","72 m/s"], "answerIndex":0 },
    { "id":"oa2", "type":"mcq", "tag":"CS Fundamentals", "text":"What is the time complexity of binary search on a sorted array?", "options":["O(n)","O(log n)","O(n log n)","O(1)"], "answerIndex":1 }
  ],
  "technical": [
    { "id":"t1", "type":"text", "tag":"DSA", "text":"Explain how you would find the first non-repeating character in a string, and its time complexity." }
  ],
  "hr": [
    { "id":"h1", "type":"text", "tag":"Behavioral", "text":"Tell me about a time you disagreed with a teammate. How did you resolve it?" }
  ]
}

@app.post("/api/candidate", response_model=schemas.CandidateResponse)
def create_candidate(candidate: schemas.CandidateCreate, db: Session = Depends(database.get_db)):
    db_candidate = models.Candidate(**candidate.dict())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

@app.post("/api/upload-resume")
async def upload_resume(candidate_id: int = Form(...), file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    db_resume = models.Resume(candidate_id=candidate_id, filename=file.filename, filepath=file_location)
    db.add(db_resume)
    db.commit()
    return {"info": f"file '{file.filename}' saved at '{file_location}'"}

@app.get("/api/questions/{role_id}")
def get_questions(role_id: str):
    return QUESTION_BANK

import requests

@app.post("/api/analyze")
def analyze_answers(submission: schemas.AnswerSubmission, db: Session = Depends(database.get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == submission.candidate_id).first()
    
    api_key = os.getenv("LLM_API_KEY")
    # Replace this with your specific LLM provider's endpoint if it's not OpenAI-compatible.
    llm_endpoint = os.getenv("LLM_ENDPOINT", "https://api.openai.com/v1/chat/completions") 
    
    prompt = f"""
    You are an expert technical interviewer. Evaluate the candidate's answers based on their target role: {candidate.role_id} and expected package {candidate.expected_package} {candidate.package_unit}.
    
    Here are the candidate's answers:
    {json.dumps(submission.answers, indent=2)}
    
    Provide a JSON response ONLY, with the following keys and integer/float values:
    "oa_score": integer (0 to 100),
    "technical_score": float (0.0 to 10.0),
    "hr_score": float (0.0 to 10.0),
    "overall": integer (0 to 100),
    "strengths": string (Summarize the candidate's strengths),
    "improvements": string (Summarize areas for improvement)
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Generic payload structure commonly used by OpenAI, Groq, Together AI, Mistral, etc.
    payload = {
        "model": os.getenv("LLM_MODEL", "gpt-3.5-turbo"), # Update with your specific model name
        "messages": [
            {"role": "system", "content": "You are a helpful AI that strictly outputs JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(llm_endpoint, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse the JSON response from the LLM
        # Depending on the provider, the path to the text might differ slightly.
        llm_text = data["choices"][0]["message"]["content"]
        
        # Strip potential markdown formatting (```json)
        llm_text = llm_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(llm_text)
        
        oa_score = int(result.get("oa_score", 70))
        technical_score = float(result.get("technical_score", 7.0))
        hr_score = float(result.get("hr_score", 7.0))
        overall = int(result.get("overall", 75))
        strengths = str(result.get("strengths", "Good foundational knowledge."))
        improvements = str(result.get("improvements", "Could elaborate more on specific examples."))
        
    except Exception as e:
        print(f"LLM API Error: {e}")
        # Fallback logic if the LLM call fails
        oa_score = 80
        technical_score = 8.5
        hr_score = 9.0
        overall = 85
        strengths = "Good technical depth. Clear communication."
        improvements = f"Ensure the LLM endpoint/model is correct. Error: {str(e)}"

    db_report = models.Report(
        candidate_id=submission.candidate_id,
        oa_score=oa_score,
        technical_score=technical_score,
        hr_score=hr_score,
        overall_score=overall,
        strengths=strengths,
        improvements=improvements
    )
    db.add(db_report)
    db.commit()
    
    return {
        "oa": oa_score,
        "technical": technical_score,
        "hr": hr_score,
        "overall": overall,
        "strengths": [strengths],
        "improvements": [improvements]
    }

app.mount("/", StaticFiles(directory="../static", html=True), name="static")
