from abc import ABC, abstractmethod
from typing import Dict, Any, Type
from ..services.research_service import ResearchContext
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from ..config import settings
import json

class BaseReportSection(ABC):
    def __init__(self, api_key: str = None):
        key = api_key if api_key else settings.GOOGLE_API_KEY
        # We use Gemini instead of Anthropic
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=key,
            max_tokens=4096,
        )

    @abstractmethod
    def get_prompt_template(self) -> str:
        pass
        
    @abstractmethod
    def get_pydantic_schema(self) -> Type[BaseModel]:
        pass

    async def generate(self, context: ResearchContext) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert business intelligence analyst. You must ground all responses in the provided research context and avoid generic answers."),
            ("human", self.get_prompt_template())
        ])
        
        schema = self.get_pydantic_schema()
        llm_with_schema = self.llm.with_structured_output(schema)
        chain = prompt | llm_with_schema
        
        result = await chain.ainvoke({
            "company_name": context.company_name,
            "description": context.description,
            "news": json.dumps(context.news),
            "key_facts": json.dumps(context.key_facts)
        })
        
        # Pydantic model to dict
        return result.model_dump()
