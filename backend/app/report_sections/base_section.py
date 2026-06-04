from abc import ABC, abstractmethod
from typing import Dict, Any, Type, Optional
from ..services.research_service import ResearchContext
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from ..config import settings
import json
import re

# Gemini models to try in order — each has its own separate daily quota
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

# Groq models to try as final fallback
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]


def _is_quota_error(e: Exception) -> bool:
    err = str(e).lower()
    return any(kw in err for kw in ("resource_exhausted", "429", "quota", "rate_limit", "rate limit"))


class BaseReportSection(ABC):
    def __init__(self, api_key: str = None, groq_api_key: str = None):
        self._gemini_key = api_key or settings.GOOGLE_API_KEY
        self._groq_key = groq_api_key

    def _make_gemini(self, model: str):
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=0,
            google_api_key=self._gemini_key,
            max_tokens=4096,
        )

    def _make_groq(self, model: str):
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model,
            temperature=0,
            groq_api_key=self._groq_key,
            max_tokens=4096,
        )

    @abstractmethod
    def get_prompt_template(self) -> str:
        pass

    @abstractmethod
    def get_pydantic_schema(self) -> Type[BaseModel]:
        pass

    async def generate(self, context: ResearchContext) -> Dict[str, Any]:
        schema = self.get_pydantic_schema()
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        schema_json_escaped = schema_json.replace("{", "{{").replace("}", "}}")

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are an expert business intelligence analyst. Ground all responses in the provided research context.

You MUST respond with a valid JSON object that exactly matches this schema:
{schema_json_escaped}

Respond with ONLY the JSON object, no markdown, no code blocks, no extra text."""),
            ("human", self.get_prompt_template())
        ])

        invoke_args = {
            "company_name": context.company_name,
            "description": context.description,
            "news": json.dumps(context.news),
            "key_facts": json.dumps(context.key_facts),
        }

        # Build ordered list of (provider, model, llm_factory) to try
        attempts = []
        for m in GEMINI_MODELS:
            attempts.append(("Gemini", m, lambda model=m: self._make_gemini(model)))
        if self._groq_key:
            for m in GROQ_MODELS:
                attempts.append(("Groq", m, lambda model=m: self._make_groq(model)))

        last_error = None
        result = None
        for provider, model_name, make_llm in attempts:
            try:
                llm = make_llm()
                chain = prompt | llm
                result = await chain.ainvoke(invoke_args)
                print(f"  ✓ Success with {provider}/{model_name}")
                break
            except Exception as e:
                last_error = e
                if _is_quota_error(e):
                    print(f"  ⚠ {provider}/{model_name} quota exhausted, trying next...")
                    continue
                else:
                    raise
        else:
            raise last_error  # type: ignore[misc]

        # Extract JSON from the response
        content = result.content
        content = re.sub(r'^```(?:json)?\s*', '', content.strip(), flags=re.MULTILINE)
        content = re.sub(r'```\s*$', '', content.strip(), flags=re.MULTILINE)
        content = content.strip()

        parsed = json.loads(content)

        # LLMs sometimes return a bare JSON list instead of wrapping it in an object
        if isinstance(parsed, list):
            parsed = {"items": parsed}

        validated = schema(**parsed)
        return validated.model_dump()
