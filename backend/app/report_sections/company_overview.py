from .base_section import BaseReportSection
from pydantic import BaseModel, Field
from typing import List

class CompanyOverviewSchema(BaseModel):
    summary: str = Field(description="Summary from research context; 200-300 words")
    industry: str
    scale: str
    geographic_presence: List[str]
    confidence_score: float

class CompanyOverviewSection(BaseReportSection):
    def get_prompt_template(self) -> str:
        return """Generate a company overview for {company_name}.
Research Context:
Description: {description}
Key Facts: {key_facts}
News: {news}
"""
    def get_pydantic_schema(self):
        return CompanyOverviewSchema
