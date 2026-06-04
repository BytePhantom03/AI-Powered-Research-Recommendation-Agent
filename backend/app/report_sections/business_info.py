from .base_section import BaseReportSection
from pydantic import BaseModel, Field
from typing import List

class BusinessInfoSchema(BaseModel):
    offerings: List[str] = Field(description="Core products or services")
    developments: List[str] = Field(description="Recent business developments based on news")
    expansion_plans: List[str]

class BusinessInfoSection(BaseReportSection):
    def get_prompt_template(self) -> str:
        return """Extract key business facts for {company_name}. Rank by recency and impact.
Research Context:
Description: {description}
Key Facts: {key_facts}
News: {news}
"""
    def get_pydantic_schema(self):
        return BusinessInfoSchema
