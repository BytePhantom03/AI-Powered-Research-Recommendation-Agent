import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Integer, BigInteger, Text, Numeric, JSON, Uuid
from .base import Base

class Report(Base):
    __tablename__ = 'reports'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=True)
    company_id = Column(Uuid(as_uuid=True), ForeignKey('companies.id'), index=True, nullable=True)
    company_name_raw = Column(String(255), nullable=False)
    status = Column(String(50), default='PENDING', index=True)
    
    section_overview = Column(JSON)
    section_business_info = Column(JSON)
    section_challenges = Column(JSON)
    section_ai_opps = Column(JSON)
    section_ceo_pitch = Column(JSON)

    research_sources = Column(JSON, default=list)
    llm_tokens_used = Column(Integer, default=0)
    generation_time_ms = Column(Integer)
    error_message = Column(Text)

    pdf_s3_key = Column(String(500))
    json_s3_key = Column(String(500))

    options = Column(JSON, default=dict)
    
    # Store live progress as JSON string directly in DB for local mode instead of Redis
    progress = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ReportEvent(Base):
    __tablename__ = 'report_events'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    report_id = Column(Uuid(as_uuid=True), ForeignKey('reports.id'), index=True)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UsageLog(Base):
    __tablename__ = 'usage_logs'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Uuid(as_uuid=True), ForeignKey('users.id'))
    action = Column(String(100))
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Numeric(10, 6), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
