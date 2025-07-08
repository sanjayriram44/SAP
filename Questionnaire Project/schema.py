 
from pydantic import BaseModel
from typing import List, Dict, Optional
 
# --- Follow-up structure ---
class FollowUp(BaseModel):
    question: str
    answer: str
 
# --- Main conversation entry ---
class ConversationEntry(BaseModel):
    question: str
    answer: str
    followups: List[FollowUp] = []
 
# --- Request body for process understanding / recommendation ---
class ConversationHistoryRequest(BaseModel):
    conversation_history: List[ConversationEntry]
 
# --- Response schema for process understanding ---
class ProcessUnderstandingResponse(BaseModel):
    summary: str
 
# --- Response schema for process recommendation ---
class ProcessRecommendationResponse(BaseModel):
    recommendation: str