from pydantic import BaseModel
from typing import Optional, Any

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
        from_attributes = True

class AnswerSubmission(BaseModel):
    round: str
    answers: Any
    candidate_id: int
