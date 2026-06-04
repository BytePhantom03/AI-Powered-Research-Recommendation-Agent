from fpdf import FPDF
import os
import re
from ..models.schemas.report import ReportResponse

# Path to DejaVu Sans font (supports Unicode including ₹, ™, etc.)
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_REGULAR = os.path.join(FONT_DIR, "DejaVuSans.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


def safe_str(text):
    """Convert to string, never return None or empty."""
    if text is None:
        return "N/A"
    return str(text) or "N/A"


def ascii_fallback(text):
    """Strip non-ASCII as last resort to prevent fpdf crashes."""
    return re.sub(r'[^\x20-\x7E\n\t]', '', safe_str(text)) or "N/A"


class PDFService:
    def generate_pdf(self, report: ReportResponse) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Try to register Unicode font (DejaVu Sans)
        use_unicode = False
        font_name = "helvetica"
        try:
            if os.path.exists(FONT_REGULAR) and os.path.exists(FONT_BOLD):
                pdf.add_font("DejaVu", "", FONT_REGULAR)
                pdf.add_font("DejaVu", "B", FONT_BOLD)
                font_name = "DejaVu"
                use_unicode = True
        except Exception:
            font_name = "helvetica"
            use_unicode = False

        def _write(text, style="", size=11):
            """Write text to PDF, with automatic ASCII fallback on failure."""
            text = safe_str(text)
            pdf.set_font(font_name, style, size)
            try:
                pdf.multi_cell(0, 8, txt=text)
            except Exception:
                # ASCII fallback - guaranteed to work with any font
                cleaned = ascii_fallback(text)
                try:
                    pdf.multi_cell(0, 8, txt=cleaned)
                except Exception:
                    # Ultimate fallback - write placeholder
                    pdf.set_font("helvetica", "", size)
                    pdf.multi_cell(0, 8, txt="[content omitted - encoding issue]")

        def add_heading(text, size=14):
            _write(text, style="B", size=size)

        def add_text(text, bold=False):
            _write(text, style="B" if bold else "", size=11)

        # Title
        try:
            pdf.set_font(font_name, "B", 16)
            pdf.cell(0, 10, safe_str(f"Company Intelligence Report: {report.company.name}"), ln=True, align="C")
        except Exception:
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, ascii_fallback(f"Company Intelligence Report: {report.company.name}"), ln=True, align="C")
        pdf.ln(5)

        sections = report.sections or {}
        overview = sections.get("company_overview") or {}
        biz = sections.get("business_info") or {}
        chal = sections.get("challenges") or {}
        ai_opps = sections.get("ai_opportunities") or {}
        pitch = sections.get("ceo_pitch") or {}

        # 1. Overview
        add_heading("1. Company Overview")
        add_text(f"Industry: {safe_str(report.company.industry)}")
        add_text(f"Scale: {safe_str(overview.get('scale'))}")
        add_text(f"Summary:\n{safe_str(overview.get('summary'))}")
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
            add_text(f"- {safe_str(item.get('challenge'))} ({safe_str(item.get('category'))})", bold=True)
            add_text(f"  Severity: {safe_str(item.get('severity'))}")
            add_text(f"  {safe_str(item.get('reasoning'))}")
            pdf.ln(2)
        pdf.ln(3)

        # 4. AI Opportunities
        add_heading("4. AI Opportunities")
        for item in ai_opps.get("items", []):
            add_text(f"- {safe_str(item.get('opportunity'))} ({safe_str(item.get('category'))})", bold=True)
            add_text(f"  Impact: {safe_str(item.get('impact'))} | Effort: {safe_str(item.get('effort'))}")
            add_text(f"  {safe_str(item.get('rationale'))}")
            pdf.ln(2)
        pdf.ln(3)

        # 5. CEO Pitch
        add_heading("5. CEO Pitch")
        add_text(safe_str(pitch.get("content")))

        return pdf.output(dest='S')
