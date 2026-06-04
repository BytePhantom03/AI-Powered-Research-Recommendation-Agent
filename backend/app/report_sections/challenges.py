from .base_section import BaseReportSection
from pydantic import BaseModel, Field
from typing import List

class ChallengeItem(BaseModel):
    category: str
    challenge: str
    reasoning: str
    severity: str = Field(description="HIGH, MEDIUM, or LOW")

class ChallengesSchema(BaseModel):
    items: List[ChallengeItem]

class ChallengesSection(BaseReportSection):
    def get_prompt_template(self) -> str:
        return """Analyze potential business challenges for {company_name} based on the research.
Research Context:
Description: {description}
Key Facts: {key_facts}
News: {news}
"""
    def get_pydantic_schema(self):
        return ChallengesSchema
