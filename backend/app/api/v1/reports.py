from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from ...dependencies import get_db_session, get_redis
from ...models.schemas.report import ReportRequest, ReportResponseAccepted, ReportStatusResponse, ReportResponse
from ...services.report_service import ReportService
from ...services.pdf_service import PDFService
import uuid

router = APIRouter()

@router.post("", response_model=ReportResponseAccepted, status_code=status.HTTP_202_ACCEPTED)
async def create_report(
    request: ReportRequest, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session), 
    redis = Depends(get_redis)
):
    report_service = ReportService(db, redis)
    return await report_service.enqueue_report(request, background_tasks)

@router.get("/{report_id}/status", response_model=ReportStatusResponse)
async def get_report_status(report_id: str, db: AsyncSession = Depends(get_db_session), redis = Depends(get_redis)):
    report_service = ReportService(db, redis)
    return await report_service.get_status(report_id)

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str, db: AsyncSession = Depends(get_db_session), redis = Depends(get_redis)):
    report_service = ReportService(db, redis)
    return await report_service.get_report(report_id)

@router.get("/{report_id}/pdf")
async def get_report_pdf(report_id: str, db: AsyncSession = Depends(get_db_session), redis = Depends(get_redis)):
    report_service = ReportService(db, redis)
    report = await report_service.get_report(report_id)
    
    pdf_service = PDFService()
    pdf_bytes = pdf_service.generate_pdf(report)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{report.company.canonical_name}_report.pdf"'}
    )
