from pydantic import BaseModel
from typing import List, Optional

class ReportBase(BaseModel):
    oa_score: int
    technical_score: float
    hr_score: float
    overall_score: int
    strengths: str
    improvements: str

class CandidateCreate(BaseModel):
    name: str
    role_id: str
    target_companies: str
    expected_package: float
    package_unit: str

class CandidateResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class AnswerSubmission(BaseModel):
    round: str
    answers: dict
    candidate_id: int
