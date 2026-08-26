import os
import pathlib
import shutil
import json
import traceback
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from google import genai

import models, schemas, database
from database import engine

# --------------- Resume text extraction helpers ---------------
def extract_text_from_pdf(filepath: str) -> str:
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
        return text.strip()
    except Exception as e:
        print(f"[PDF Extract Error] {e}")
        return ""

def extract_text_from_docx(filepath: str) -> str:
    try:
        import docx
        doc = docx.Document(filepath)
        text = "\n".join([p.text for p in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"[DOCX Extract Error] {e}")
        return ""

def extract_resume_text(filepath: str) -> str:
    fp = filepath.lower()
    if fp.endswith(".pdf"):
        return extract_text_from_pdf(filepath)
    elif fp.endswith(".docx") or fp.endswith(".doc"):
        return extract_text_from_docx(filepath)
    else:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        except:
            return ""

# --------------- Create DB tables ---------------
models.Base.metadata.create_all(bind=engine)

# --------------- App setup ---------------
app = FastAPI(title="Prepped – Interview Prep Bot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = pathlib.Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# --------------- Configure Gemini ---------------
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
gemini_client = None
if LLM_API_KEY:
    gemini_client = genai.Client(api_key=LLM_API_KEY)

GEMINI_MODEL = "gemini-3.6-flash"

# --------------- Fallback Question Bank (used when AI fails) ---------------
FALLBACK_QUESTIONS = {
    "oa": [
        {"id":"oa1","type":"mcq","tag":"Aptitude","text":"A train 120m long crosses a pole in 6 seconds. What is its speed?","options":["20 m/s","24 m/s","18 m/s","72 m/s"],"answerIndex":0},
        {"id":"oa2","type":"mcq","tag":"CS Fundamentals","text":"What is the time complexity of binary search on a sorted array?","options":["O(n)","O(log n)","O(n log n)","O(1)"],"answerIndex":1},
        {"id":"oa3","type":"mcq","tag":"Logical Reasoning","text":"If all roses are flowers and some flowers fade quickly, which statement is definitely true?","options":["All roses fade quickly","Some roses fade quickly","No roses fade quickly","Some roses may fade quickly"],"answerIndex":3},
        {"id":"oa4","type":"mcq","tag":"Data Structures","text":"Which data structure uses FIFO (First In First Out)?","options":["Stack","Queue","Binary Tree","Hash Map"],"answerIndex":1},
        {"id":"oa5","type":"mcq","tag":"Networking","text":"Which protocol is used for secure web communication?","options":["HTTP","FTP","HTTPS","SMTP"],"answerIndex":2},
        {"id":"oa6","type":"mcq","tag":"OS Concepts","text":"Which scheduling algorithm may cause starvation?","options":["Round Robin","FCFS","Shortest Job First","All of the above"],"answerIndex":2},
        {"id":"oa7","type":"mcq","tag":"DBMS","text":"What does ACID stand for in database transactions?","options":["Atomicity, Consistency, Isolation, Durability","Atomicity, Concurrency, Isolation, Durability","Association, Consistency, Isolation, Durability","Atomicity, Consistency, Integration, Durability"],"answerIndex":0},
        {"id":"oa8","type":"mcq","tag":"Programming","text":"What will be the output of: print(type([]) is list)","options":["True","False","Error","None"],"answerIndex":0}
    ],
    "technical": [
        {"id":"t1","type":"text","tag":"DSA","text":"Explain how you would find the first non-repeating character in a string and analyse its time complexity."},
        {"id":"t2","type":"text","tag":"System Design","text":"Design a URL shortener service like bit.ly. Describe the high-level architecture."},
        {"id":"t3","type":"text","tag":"Problem Solving","text":"Given an array of integers, how would you find two numbers that add up to a specific target?"},
        {"id":"t4","type":"text","tag":"OOP Concepts","text":"Explain the SOLID principles with real-world examples."},
        {"id":"t5","type":"text","tag":"Database","text":"What is the difference between SQL and NoSQL databases? When would you choose one over the other?"}
    ],
    "hr": [
        {"id":"h1","type":"text","tag":"Behavioral","text":"Tell me about a time you disagreed with a teammate. How did you resolve it?"},
        {"id":"h2","type":"text","tag":"Motivation","text":"Why do you want to work at this company? What excites you about the role?"},
        {"id":"h3","type":"text","tag":"Leadership","text":"Describe a situation where you had to lead a project under a tight deadline."},
        {"id":"h4","type":"text","tag":"Self-Awareness","text":"What is your biggest weakness? How are you working to improve it?"},
        {"id":"h5","type":"text","tag":"Culture Fit","text":"Where do you see yourself in 5 years? How does this role fit into your career plan?"}
    ]
}

# --------------- API Routes ---------------

@app.get("/")
def root():
    return RedirectResponse(url="/index.html")


@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload resume immediately on page 1. Returns a resume_path for later use."""
    file_location = UPLOAD_DIR / file.filename
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    return {
        "success": True,
        "filename": file.filename,
        "filepath": str(file_location)
    }


@app.post("/api/candidate", response_model=schemas.CandidateResponse)
def create_candidate(candidate: schemas.CandidateCreate, db: Session = Depends(database.get_db)):
    db_candidate = models.Candidate(**candidate.model_dump())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate


@app.post("/api/generate-questions")
def generate_questions(payload: dict, db: Session = Depends(database.get_db)):
    """
    Generate personalized interview questions using Gemini AI based on the resume.
    Expects: { "role_id": "sde", "resume_path": "uploads/resume.pdf" }
    """
    role_id = payload.get("role_id", "sde")
    resume_path = payload.get("resume_path", "")
    candidate_id = payload.get("candidate_id")

    # Extract resume text
    resume_text = ""
    if resume_path and os.path.exists(resume_path):
        resume_text = extract_resume_text(resume_path)
        print(f"[Resume] Extracted {len(resume_text)} chars from {resume_path}")
    else:
        print(f"[Resume] No valid resume path: '{resume_path}'")

    if not resume_text:
        resume_text = "No resume provided."

    # Truncate if too long (Gemini has token limits)
    if len(resume_text) > 8000:
        resume_text = resume_text[:8000] + "\n... (truncated)"

    role_names = {
        "sde": "Software Engineer", "frontend": "Frontend Developer",
        "data": "Data Scientist", "mlai": "ML / AI Engineer",
        "devops": "DevOps Engineer", "product": "Product Manager",
        "business": "Business Analyst", "security": "Cybersecurity Analyst",
        "qa": "QA / SDET"
    }
    role_title = role_names.get(role_id, role_id)

    prompt = f"""You are an expert technical interviewer preparing a mock interview for a "{role_title}" position.

Here is the candidate's resume:
---
{resume_text}
---

Generate personalized interview questions based on the candidate's resume, skills, and experience.

IMPORTANT: Respond with ONLY valid JSON (no markdown, no code fences, no explanation).
Use this EXACT structure:

{{
  "oa": [
    {{"id":"oa1","type":"mcq","tag":"<topic>","text":"<question>","options":["A","B","C","D"],"answerIndex":<0-3>}},
    {{"id":"oa2","type":"mcq","tag":"<topic>","text":"<question>","options":["A","B","C","D"],"answerIndex":<0-3>}},
    {{"id":"oa3","type":"mcq","tag":"<topic>","text":"<question>","options":["A","B","C","D"],"answerIndex":<0-3>}},
    {{"id":"oa4","type":"mcq","tag":"<topic>","text":"<question>","options":["A","B","C","D"],"answerIndex":<0-3>}},
    {{"id":"oa5","type":"mcq","tag":"<topic>","text":"<question>","options":["A","B","C","D"],"answerIndex":<0-3>}},
    {{"id":"oa6","type":"mcq","tag":"<topic>","text":"<question>","options":["A","B","C","D"],"answerIndex":<0-3>}},
    {{"id":"oa7","type":"mcq","tag":"<topic>","text":"<question>","options":["A","B","C","D"],"answerIndex":<0-3>}},
    {{"id":"oa8","type":"mcq","tag":"<topic>","text":"<question>","options":["A","B","C","D"],"answerIndex":<0-3>}}
  ],
  "technical": [
    {{"id":"t1","type":"text","tag":"<topic>","text":"<question>"}},
    {{"id":"t2","type":"text","tag":"<topic>","text":"<question>"}},
    {{"id":"t3","type":"text","tag":"<topic>","text":"<question>"}},
    {{"id":"t4","type":"text","tag":"<topic>","text":"<question>"}},
    {{"id":"t5","type":"text","tag":"<topic>","text":"<question>"}}
  ],
  "hr": [
    {{"id":"h1","type":"text","tag":"<topic>","text":"<question>"}},
    {{"id":"h2","type":"text","tag":"<topic>","text":"<question>"}},
    {{"id":"h3","type":"text","tag":"<topic>","text":"<question>"}},
    {{"id":"h4","type":"text","tag":"<topic>","text":"<question>"}},
    {{"id":"h5","type":"text","tag":"<topic>","text":"<question>"}}
  ]
}}

Rules:
- OA questions: 8 MCQ questions testing aptitude, CS fundamentals, and skills listed on the resume. Each must have exactly 4 options with a correct answerIndex (0-3).
- Technical questions: 5 open-ended questions about technologies, projects, and skills from the resume. Ask them to explain, design, or solve problems related to their actual experience.
- HR questions: 5 behavioral/motivational questions tailored to their background and career trajectory.
- Make questions specific to what's on the resume (projects, tech stack, experience level).
- Tag each question with a relevant topic label."""

    try:
        if gemini_client:
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            llm_text = response.text.strip()

            # Strip markdown code fences
            if llm_text.startswith("```"):
                lines = llm_text.split("\n")
                llm_text = "\n".join(lines[1:])
            if llm_text.endswith("```"):
                llm_text = llm_text[:-3]
            llm_text = llm_text.strip()

            questions = json.loads(llm_text)
            print(f"[Gemini] Generated {len(questions.get('oa',[]))} OA, {len(questions.get('technical',[]))} Tech, {len(questions.get('hr',[]))} HR questions")
        else:
            print("[Warning] No Gemini client. Returning fallback questions.")
            questions = FALLBACK_QUESTIONS
    except Exception as e:
        print(f"[Gemini Question Gen Error] {e}")
        traceback.print_exc()
        questions = FALLBACK_QUESTIONS

    if candidate_id:
        for r_key, r_qs in questions.items():
            for q in r_qs:
                db_q = models.InterviewQA(
                    candidate_id=candidate_id,
                    round=r_key,
                    question_id=q["id"],
                    question_text=q["text"]
                )
                db.add(db_q)
        db.commit()

    return questions


@app.get("/api/questions/{role_id}")
def get_questions(role_id: str):
    """Fallback endpoint — returns static questions if AI generation isn't used."""
    return FALLBACK_QUESTIONS


@app.post("/api/analyze")
def analyze_answers(submission: schemas.AnswerSubmission, db: Session = Depends(database.get_db)):
    candidate = None
    if submission.candidate_id > 0:
        candidate = db.query(models.Candidate).filter(models.Candidate.id == submission.candidate_id).first()
        
        # update answers in db
        if isinstance(submission.answers, dict):
            for r_key, r_ans in submission.answers.items():
                if isinstance(r_ans, dict):
                    for q_id, a_text in r_ans.items():
                        db.query(models.InterviewQA).filter(
                            models.InterviewQA.candidate_id == submission.candidate_id,
                            models.InterviewQA.round == r_key,
                            models.InterviewQA.question_id == q_id
                        ).update({"answer_text": str(a_text)})
            db.commit()

    role_name = candidate.role_id if candidate else "general"
    pkg_info = f"{candidate.expected_package} {candidate.package_unit}" if candidate else "not specified"

    prompt = f"""You are an expert technical interviewer and career coach.
Evaluate the following candidate's mock interview answers.

Target Role: {role_name}
Expected Package: {pkg_info}

Candidate's Answers (JSON):
{json.dumps(submission.answers, indent=2)}

IMPORTANT: Respond with ONLY valid JSON (no markdown, no explanation, no code fences).
Use this exact structure:
{{
  "oa_score": <integer 0-100>,
  "technical_score": <float 0.0-10.0>,
  "hr_score": <float 0.0-10.0>,
  "overall": <integer 0-100>,
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "improvements": ["improvement 1", "improvement 2", "improvement 3"],
  "career_suggestions": [
    {{"field": "<field name>", "reason": "<why this field suits the candidate>"}},
    {{"field": "<field name>", "reason": "<why this field suits the candidate>"}},
    {{"field": "<field name>", "reason": "<why this field suits the candidate>"}}
  ]
}}

Score fairly based on correctness, depth, communication, and relevance to the target role.
If answers are empty or very short, give lower scores accordingly.
For career_suggestions: Based on the candidate's answers, suggest 3 career fields or specializations they should focus on, with a reason for each."""

    # Defaults
    oa_score = 72
    technical_score = 7.0
    hr_score = 7.5
    overall = 74
    strengths_list = ["Shows willingness to learn", "Attempted all questions", "Basic concepts are clear"]
    improvements_list = ["Provide more detailed explanations", "Use concrete examples", "Practice system design"]
    career_suggestions = [
        {"field": "Full-Stack Development", "reason": "Strong fundamentals in both frontend and backend technologies."},
        {"field": "Cloud Engineering", "reason": "Good understanding of scalable architectures and modern tooling."},
        {"field": "Technical Consulting", "reason": "Clear communication skills and ability to explain complex concepts."}
    ]

    try:
        if gemini_client:
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            llm_text = response.text.strip()

            if llm_text.startswith("```"):
                lines = llm_text.split("\n")
                llm_text = "\n".join(lines[1:])
            if llm_text.endswith("```"):
                llm_text = llm_text[:-3]
            llm_text = llm_text.strip()

            result = json.loads(llm_text)

            oa_score = int(result.get("oa_score", 72))
            technical_score = float(result.get("technical_score", 7.0))
            hr_score = float(result.get("hr_score", 7.5))
            overall = int(result.get("overall", 74))

            s = result.get("strengths", strengths_list)
            strengths_list = s if isinstance(s, list) else [s]

            imp = result.get("improvements", improvements_list)
            improvements_list = imp if isinstance(imp, list) else [imp]

            cs = result.get("career_suggestions", career_suggestions)
            if isinstance(cs, list):
                career_suggestions = cs

            print(f"[Gemini] Analysis successful — overall score: {overall}")
        else:
            print("[Warning] No Gemini client. Using fallback scores.")
    except Exception as e:
        print(f"[Gemini Error] {e}")

    db_report = models.Report(
        candidate_id=submission.candidate_id if submission.candidate_id > 0 else None,
        oa_score=oa_score,
        technical_score=technical_score,
        hr_score=hr_score,
        overall_score=overall,
        strengths=json.dumps(strengths_list),
        improvements=json.dumps(improvements_list)
    )
    db.add(db_report)
    db.commit()

    return {
        "oa": oa_score,
        "technical": technical_score,
        "hr": hr_score,
        "overall": overall,
        "strengths": strengths_list,
        "improvements": improvements_list,
        "career_suggestions": career_suggestions
    }

# --------------- Static files (MUST be last) ---------------
app.mount("/", StaticFiles(directory=str(pathlib.Path(__file__).resolve().parent.parent / "static"), html=True), name="static")
