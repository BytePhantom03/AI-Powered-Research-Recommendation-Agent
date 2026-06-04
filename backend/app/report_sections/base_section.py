from abc import ABC, abstractmethod
from typing import Dict, Any, Type
from ..services.research_service import ResearchContext
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from ..config import settings
import json
import re

# Models to try in order — each has its own separate daily quota
FALLBACK_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]


class BaseReportSection(ABC):
    def __init__(self, api_key: str = None):
        self._api_key = api_key if api_key else settings.GOOGLE_API_KEY

    def _make_llm(self, model: str):
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=0,
            google_api_key=self._api_key,
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

        # Try each model until one succeeds
        last_error = None
        for model_name in FALLBACK_MODELS:
            try:
                llm = self._make_llm(model_name)
                chain = prompt | llm
                result = await chain.ainvoke(invoke_args)
                print(f"  ✓ Success with model: {model_name}")
                break
            except Exception as e:
                last_error = e
                err_str = str(e).lower()
                # Only fallback on quota/rate-limit errors; re-raise others immediately
                if "resource_exhausted" in err_str or "429" in err_str or "quota" in err_str:
                    print(f"  ⚠ {model_name} quota exhausted, trying next model...")
                    continue
                else:
                    raise
        else:
            # All models failed
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
