from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
from datetime import datetime

class StudentProfile(BaseModel):
    name: str
    email: EmailStr
    interests: List[str]
    grades: Dict[str, float]

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    interests: Optional[List[str]] = None
    grades: Optional[Dict[str, float]] = None

class Program(BaseModel):
    id: str
    name: str
    description: str
    tags: List[str]
    skills: List[str]
    requirements: Dict

class Recommendation(BaseModel):
    program_id: str
    program_name: str
    program_description: str
    score: float
    explanation: str
    tags: List[str]
    skills: List[str]

class FeedbackSubmit(BaseModel):
    program_id: str
    rating: Optional[int] = None
    clicked: bool = False
    accepted: bool = False

class RecommendationRequest(BaseModel):
    student_id: str
    top_k: int = 5
