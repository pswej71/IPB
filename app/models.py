from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), index=True)
    role_id = Column(String(50))
    target_companies = Column(String(500))
    expected_package = Column(Float)
    package_unit = Column(String(10))

    resume = relationship("Resume", back_populates="candidate", uselist=False)
    report = relationship("Report", back_populates="candidate", uselist=False)

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    filename = Column(String(255))
    filepath = Column(String(255))
    
    candidate = relationship("Candidate", back_populates="resume")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    oa_score = Column(Integer)
    technical_score = Column(Float)
    hr_score = Column(Float)
    overall_score = Column(Integer)
    strengths = Column(Text)
    improvements = Column(Text)

    candidate = relationship("Candidate", back_populates="report")

class InterviewQA(Base):
    __tablename__ = "interview_qa"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    round = Column(String(50))
    question_id = Column(String(50))
    question_text = Column(Text)
    answer_text = Column(Text, nullable=True)

    candidate = relationship("Candidate")
