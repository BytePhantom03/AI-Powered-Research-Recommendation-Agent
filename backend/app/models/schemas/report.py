from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class ReportOptions(BaseModel):
    sections: List[str] = ["overview", "business_info", "challenges", "ai_opportunities", "ceo_pitch"]
    depth: str = "standard"
    export_format: List[str] = ["pdf", "json"]
    api_keys: Optional[Dict[str, str]] = None

class ReportRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=100)
    options: ReportOptions = Field(default_factory=ReportOptions)

class ReportResponseAccepted(BaseModel):
    report_id: UUID
    status: str
    estimated_duration_seconds: int
    status_url: str
    websocket_channel: str
    created_at: datetime

class ReportStatusProgress(BaseModel):
    current_step: int
    total_steps: int
    current_task: str
    percentage: int

class ReportStatusResponse(BaseModel):
    report_id: UUID
    status: str
    progress: Optional[ReportStatusProgress] = None

class CompanySchema(BaseModel):
    name: str
    canonical_name: str
    industry: Optional[str] = None
    headquarters: Optional[str] = None

class ReportMetadataSchema(BaseModel):
    generation_time_seconds: Optional[int] = None
    sources_used: Optional[int] = None
    llm_tokens_used: Optional[int] = None
    export_urls: Optional[Dict[str, str]] = None

class ReportResponse(BaseModel):
    report_id: UUID
    status: str
    company: CompanySchema
    sections: Dict[str, Any]
    metadata: ReportMetadataSchema
    created_at: datetime
    completed_at: Optional[datetime] = None
