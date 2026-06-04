from fpdf import FPDF
import os
from ..models.schemas.report import ReportResponse

# Path to DejaVu Sans font (supports Unicode including ₹, ™, etc.)
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_REGULAR = os.path.join(FONT_DIR, "DejaVuSans.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


class PDFService:
    def generate_pdf(self, report: ReportResponse) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Register Unicode font
        if os.path.exists(FONT_REGULAR):
            pdf.add_font("DejaVu", "", FONT_REGULAR, uni=True)
            pdf.add_font("DejaVu", "B", FONT_BOLD, uni=True)
            font_name = "DejaVu"
        else:
            # Fallback to helvetica if font not installed (local dev)
            font_name = "helvetica"

        def add_heading(text, size=14):
            pdf.set_font(font_name, "B", size)
            pdf.multi_cell(0, 10, txt=str(text or "N/A"))

        def add_text(text, bold=False):
            pdf.set_font(font_name, "B" if bold else "", 11)
            pdf.multi_cell(0, 8, txt=str(text or "N/A"))

        # Title
        pdf.set_font(font_name, "B", 16)
        pdf.cell(0, 10, str(f"Company Intelligence Report: {report.company.name}"), ln=True, align="C")
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
