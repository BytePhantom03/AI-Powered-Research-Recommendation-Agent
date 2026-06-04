from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...models.db.report import Report
from ...services.research_service import ResearchService
from ...report_sections import (
    CompanyOverviewSection,
    BusinessInfoSection,
    ChallengesSection,
    AIOpportunitiesSection,
    CEOPitchSection
)
from datetime import datetime
import time
import asyncio

async def update_progress(db: AsyncSession, report: Report, step: int, total: int, task_name: str):
    progress = {
        "current_step": step,
        "total_steps": total,
        "current_task": task_name,
        "percentage": int((step / total) * 100)
    }
    report.progress = progress
    await db.commit()

async def generate_report_task(report_id: str):
    # Need to create a new session for the background task
    from ...dependencies import async_session_maker
    
    async with async_session_maker() as db:
        result = await db.execute(select(Report).filter(Report.id == report_id))
        report = result.scalars().first()
        if not report:
            return
            
        report.status = "RESEARCHING"
        report.started_at = datetime.now()
        await db.commit()
        
        await update_progress(db, report, 1, 6, "Gathering web research via Tavily")

        try:
            start_time = time.time()
            
            # Extract custom API keys if provided
            opts = report.options or {}
            api_keys = opts.get("api_keys") or {}
            google_key = api_keys.get("gemini")
            tavily_key = api_keys.get("tavily")
            groq_key = api_keys.get("groq")
            
            # 1. Research Phase
            research_service = ResearchService(api_key=tavily_key)
            context = await research_service.fetch_context(report.company_name_raw)
            
            report.status = "PROCESSING"
            await db.commit()
            
            # 2. AI Sections
            sections = [
                ("overview", CompanyOverviewSection(api_key=google_key, groq_api_key=groq_key), "Generating Company Overview"),
                ("business_info", BusinessInfoSection(api_key=google_key, groq_api_key=groq_key), "Extracting Business Information"),
                ("challenges", ChallengesSection(api_key=google_key, groq_api_key=groq_key), "Analyzing Challenges"),
                ("ai_opportunities", AIOpportunitiesSection(api_key=google_key, groq_api_key=groq_key), "Identifying AI Opportunities"),
                ("ceo_pitch", CEOPitchSection(api_key=google_key, groq_api_key=groq_key), "Drafting CEO Pitch")
            ]
            
            results = {}
            for idx, (section_key, section_obj, task_msg) in enumerate(sections):
                await update_progress(db, report, idx + 2, 6, task_msg)
                section_res = await section_obj.generate(context)
                results[section_key] = section_res
                # Delay between API calls to respect Gemini free tier rate limits (5 req/min)
                if idx < len(sections) - 1:
                    await asyncio.sleep(15)
                
            report.section_overview = results.get("overview")
            report.section_business_info = results.get("business_info")
            report.section_challenges = results.get("challenges")
            report.section_ai_opps = results.get("ai_opportunities")
            report.section_ceo_pitch = results.get("ceo_pitch")
            
            report.status = "COMPLETE"
            report.completed_at = datetime.now()
            report.generation_time_ms = int((time.time() - start_time) * 1000)
            report.research_sources = [r.get("url") for r in context.raw_results if r.get("url")]
            
            await update_progress(db, report, 6, 6, "Report Complete")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            report.status = "FAILED"
            report.error_message = str(e)
            await db.commit()
            print(f"Task failed: {e}")
