from .base_section import BaseReportSection
from pydantic import BaseModel, Field

class CEOPitchSchema(BaseModel):
    content: str = Field(description="Persuasive one-pager in first-person voice referencing actual company data")
    word_count: int

class CEOPitchSection(BaseReportSection):
    def get_prompt_template(self) -> str:
        return """Write a persuasive CEO-level pitch to sell an AI transformation to {company_name}.
Research Context:
Description: {description}
Key Facts: {key_facts}
News: {news}
"""
    def get_pydantic_schema(self):
        return CEOPitchSchema
