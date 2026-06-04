from dataclasses import dataclass
from typing import List, Dict, Any
from tavily import TavilyClient
from ..config import settings
import asyncio

@dataclass
class ResearchContext:
    company_name: str
    description: str
    news: List[Dict[str, str]]
    key_facts: List[str]
    raw_results: List[Dict[str, Any]]

class ResearchService:
    def __init__(self, api_key: str = None):
        key = api_key if api_key else settings.TAVILY_API_KEY
        self.tavily = TavilyClient(api_key=key)

    async def fetch_context(self, company_name: str) -> ResearchContext:
        query_company = f"{company_name} company overview business model"
        query_news = f"{company_name} recent news updates"
        
        # We can run these concurrently using to_thread
        overview_res, news_res = await asyncio.gather(
            asyncio.to_thread(self.tavily.search, query=query_company, search_depth="advanced", max_results=5),
            asyncio.to_thread(self.tavily.search, query=query_news, search_depth="basic", max_results=5)
        )
        
        raw_results = []
        raw_results.extend(overview_res.get("results", []))
        raw_results.extend(news_res.get("results", []))
        
        # Extract basic info
        description = overview_res.get("answer", "")
        if not description:
            # Fallback to concatenating top snippets
            description = " ".join([r.get("content", "") for r in overview_res.get("results", [])[:3]])

        news = [{"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("content", "")} 
                for r in news_res.get("results", [])]
                
        key_facts = [r.get("content", "") for r in overview_res.get("results", [])]

        return ResearchContext(
            company_name=company_name,
            description=description,
            news=news,
            key_facts=key_facts,
            raw_results=raw_results
        )
