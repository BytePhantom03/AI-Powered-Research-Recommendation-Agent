from fpdf import FPDF
import re
from ..models.schemas.report import ReportResponse


def sanitize_text(text):
    """Strip all non-ASCII characters to guarantee fpdf2 can render the text."""
    if text is None:
        return "N/A"
    text = str(text)
    # Keep only printable ASCII (space through tilde, plus newlines/tabs)
    text = re.sub(r'[^\x20-\x7E\n\t]', '', text)
    # Collapse multiple spaces
    text = re.sub(r'  +', ' ', text)
    return text.strip() or "N/A"


class PDFService:
    def generate_pdf(self, report: ReportResponse) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        def add_heading(text, size=14):
            pdf.set_font("helvetica", "B", size)
            pdf.multi_cell(0, 10, txt=sanitize_text(text))

        def add_text(text, bold=False):
            pdf.set_font("helvetica", "B" if bold else "", 11)
            pdf.multi_cell(0, 8, txt=sanitize_text(text))

        # Title
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, sanitize_text(f"Company Intelligence Report: {report.company.name}"), ln=True, align="C")
        pdf.ln(5)

        sections = report.sections or {}
        overview = sections.get("company_overview") or {}
        biz = sections.get("business_info") or {}
        chal = sections.get("challenges") or {}
        ai_opps = sections.get("ai_opportunities") or {}
        pitch = sections.get("ceo_pitch") or {}

        # 1. Overview
        add_heading("1. Company Overview")
        add_text(f"Industry: {report.company.industry or 'N/A'}")
        add_text(f"Scale: {overview.get('scale', 'N/A')}")
        add_text(f"Summary:\n{overview.get('summary', 'N/A')}")
        pdf.ln(5)

        # 2. Business Info
        add_heading("2. Business Information")
        if biz.get("offerings"):
            add_text("Offerings:", bold=True)
            for item in biz["offerings"]:
                add_text(f"  - {item}")
        if biz.get("developments"):
            add_text("Recent Developments:", bold=True)
            for item in biz["developments"]:
                add_text(f"  - {item}")
        if biz.get("expansion_plans"):
            add_text("Expansion Plans:", bold=True)
            for item in biz["expansion_plans"]:
                add_text(f"  - {item}")
        pdf.ln(5)

        # 3. Challenges
        add_heading("3. Business Challenges")
        for item in chal.get("items", []):
            add_text(f"- {item.get('challenge', '')} ({item.get('category', '')})", bold=True)
            add_text(f"  Severity: {item.get('severity', 'N/A')}")
            add_text(f"  {item.get('reasoning', '')}")
            pdf.ln(2)
        pdf.ln(3)

        # 4. AI Opportunities
        add_heading("4. AI Opportunities")
        for item in ai_opps.get("items", []):
            add_text(f"- {item.get('opportunity', '')} ({item.get('category', '')})", bold=True)
            add_text(f"  Impact: {item.get('impact', 'N/A')} | Effort: {item.get('effort', 'N/A')}")
            add_text(f"  {item.get('rationale', '')}")
            pdf.ln(2)
        pdf.ln(3)

        # 5. CEO Pitch
        add_heading("5. CEO Pitch")
        add_text(pitch.get("content", "N/A"))

        return pdf.output(dest='S')
