from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str
    content: str

class HoneypotRequest(BaseModel):
    conversation_id: Optional[str] = None
    messages: Optional[List[Message]] = None

class EngagementMetrics(BaseModel):
    turns: int
    duration_seconds: int

class ExtractedIntelligence(BaseModel):
    upi_ids: List[str]
    bank_accounts: List[str]
    phishing_urls: List[str]

class HoneypotResponse(BaseModel):
    scam_detected: bool
    confidence: float
    engagement_metrics: EngagementMetrics
    extracted_intelligence: ExtractedIntelligence
