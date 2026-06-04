from .base_section import BaseReportSection
from pydantic import BaseModel, Field
from typing import List

class AIOpportunityItem(BaseModel):
    opportunity: str = Field(description="Specific AI solution mapping to challenges")
    category: str
    impact: str = Field(description="HIGH, MEDIUM, or LOW")
    effort: str = Field(description="HIGH, MEDIUM, or LOW")
    rationale: str = Field(description="Rationale based on company data")

class AIOpportunitiesSchema(BaseModel):
    items: List[AIOpportunityItem]

class AIOpportunitiesSection(BaseReportSection):
    def get_prompt_template(self) -> str:
        return """Propose AI opportunities for {company_name}. Ensure these are highly specific to the company, avoiding generic answers.
Research Context:
Description: {description}
Key Facts: {key_facts}
News: {news}
"""
    def get_pydantic_schema(self):
        return AIOpportunitiesSchema
