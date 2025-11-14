from pydantic import BaseModel, validator
from typing import Any, Dict, List, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    user_id: Optional[str] = None  # Thêm user_id để lưu lịch sử

class MessageResponse(BaseModel):
    content: str
    reply: str  # Thêm field reply để tương thích với frontend
    agent: str

class AgentEvent(BaseModel):
    id: str
    type: str
    agent: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None

class GuardrailCheck(BaseModel):
    id: str
    name: str
    input: str
    reasoning: str
    passed: bool
    timestamp: float

class ChatResponse(BaseModel):
    conversation_id: str
    current_agent: str
    messages: List[MessageResponse]
    events: List[AgentEvent]
    context: Dict[str, Any]
    agents: List[Dict[str, Any]]
    guardrails: List[GuardrailCheck] = []
    reply: Optional[str] = None  # Thêm field reply chính để tương thích với frontend
    metadata: Optional[Dict[str, Any]] = None  # Thêm metadata để hỗ trợ requires_support_form

class User(BaseModel):
    username: str
    password: str

class ChatHistory(BaseModel):
    conversation_id: str
    user_id: str
    question: str
    answer: str
    agent: str
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None
    events: Optional[List[Dict[str, Any]]] = None

class TechnicalErrorReport(BaseModel):
    name: str
    organization: str
    phone: Optional[str] = None
    email: Optional[str] = None
    error_content: str
    image_url: Optional[str] = None
    timestamp: Optional[datetime] = None

class TechnicalErrorReportCreate(BaseModel):
    name: str
    organization: str
    phone: Optional[str] = None
    email: Optional[str] = None
    error_content: str
    image_url: Optional[str] = None
    
    @validator('phone', 'email', 'image_url', pre=True)
    def convert_empty_string_to_none(cls, v):
        """Convert empty strings and null values to None"""
        if v == "" or v is None or v == "null":
            return None
        return v
    
    @validator('name', 'organization', 'error_content', pre=True)
    def strip_strings(cls, v):
        """Strip whitespace from required string fields"""
        if isinstance(v, str):
            return v.strip()
        return v

