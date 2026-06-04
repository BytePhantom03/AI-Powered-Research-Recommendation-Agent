from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, BackgroundTasks
from ..models.db.report import Report
from ..models.db.company import Company
from ..models.schemas.report import ReportRequest, ReportResponseAccepted, ReportStatusResponse, ReportResponse
from ..workers.tasks.report_tasks import generate_report_task
from ..utils.company_resolver import resolve_company_slug
from datetime import datetime
from ..dependencies import async_session_maker
import uuid

class ReportService:
    def __init__(self, db: AsyncSession, redis=None):
        self.db = db
        # redis is ignored for local fallback

    async def enqueue_report(self, request: ReportRequest, background_tasks: BackgroundTasks) -> ReportResponseAccepted:
        slug = resolve_company_slug(request.company_name)
        
        # Upsert company
        result = await self.db.execute(select(Company).filter(Company.canonical_slug == slug))
        company = result.scalars().first()
        if not company:
            company = Company(
                canonical_slug=slug,
                display_name=request.company_name
            )
            self.db.add(company)
            await self.db.flush()
        
        # Create report record
        report = Report(
            company_id=company.id,
            company_name_raw=request.company_name,
            status="PENDING",
            options=request.options.model_dump()
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        
        # Enqueue task to background
        background_tasks.add_task(generate_report_task, str(report.id))
        
        return ReportResponseAccepted(
            report_id=report.id,
            status=report.status,
            estimated_duration_seconds=45,
            status_url=f"/v1/reports/{report.id}/status",
            websocket_channel=f"wss://api.researchagent.io/ws/{report.id}",
            created_at=report.created_at or datetime.now()
        )

    async def get_status(self, report_id: str) -> ReportStatusResponse:
        result = await self.db.execute(select(Report).filter(Report.id == report_id))
        report = result.scalars().first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return ReportStatusResponse(
            report_id=report.id,
            status=report.status,
            progress=report.progress
        )

    async def get_report(self, report_id: str) -> ReportResponse:
        result = await self.db.execute(select(Report).filter(Report.id == report_id))
        report = result.scalars().first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
            
        if report.status != "COMPLETE":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Report is not complete. Current status: {report.status}")
        
        # Fetch company
        result = await self.db.execute(select(Company).filter(Company.id == report.company_id))
        company = result.scalars().first()
        
        return ReportResponse(
            report_id=report.id,
            status=report.status,
            company={
                "name": company.display_name,
                "canonical_name": company.canonical_slug,
                "industry": company.industry,
                "headquarters": company.headquarters
            },
            sections={
                "company_overview": report.section_overview,
                "business_info": report.section_business_info,
                "challenges": report.section_challenges,
                "ai_opportunities": report.section_ai_opps,
                "ceo_pitch": report.section_ceo_pitch,
            },
            metadata={
                "generation_time_seconds": (report.generation_time_ms // 1000) if report.generation_time_ms else None,
                "sources_used": len(report.research_sources) if report.research_sources else 0,
                "llm_tokens_used": report.llm_tokens_used,
                "export_urls": {}
            },
            created_at=report.created_at,
            completed_at=report.completed_at
        )
