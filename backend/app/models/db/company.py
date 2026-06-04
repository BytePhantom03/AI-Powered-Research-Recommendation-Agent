import uuid
from sqlalchemy import Column, String, DateTime, func, JSON
from .base import Base
from .guid import GUID

class Company(Base):
    __tablename__ = 'companies'

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    canonical_slug = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    aliases = Column(JSON, default=list)  # Replaced ARRAY with JSON for SQLite
    industry = Column(String(255))
    headquarters = Column(String(255))
    website_url = Column(String(500))
    metadata_ = Column("metadata", JSON, default=dict) # Replaced JSONB with JSON
    last_researched = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
