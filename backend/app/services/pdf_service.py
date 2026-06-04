from fpdf import FPDF
import io
from ..models.schemas.report import ReportResponse

class PDFService:
    def generate_pdf(self, report: ReportResponse) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Helper for adding text safely
        def add_text(text, font_family="helvetica", style="", size=12):
            if text is None:
                text = "N/A"
            text = str(text)
            # Remove characters that can't be rendered in latin-1
            text = text.encode('latin-1', 'replace').decode('latin-1')
            # Replace any remaining problematic characters
            text = text.replace('\x00', '')
            pdf.set_font(font_family, style, size)
            try:
                pdf.multi_cell(0, 10, txt=text)
            except Exception:
                # Fallback: write line by line
                for line in text.split('\n'):
                    try:
                        pdf.multi_cell(0, 10, txt=line[:200] if line else " ")
                    except Exception:
                        pdf.multi_cell(0, 10, txt="[content could not be rendered]")
            
        pdf.set_font("helvetica", "B", 16)
        title = str(report.company.name).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 10, f"Company Intelligence Report: {title}", ln=True, align="C")
        pdf.ln(5)
        
        sections = report.sections or {}
        overview = sections.get("company_overview", {})
        biz = sections.get("business_info", {})
        chal = sections.get("challenges", {})
        ai = sections.get("ai_opportunities", {})
        pitch = sections.get("ceo_pitch", {})

        # Overview
        add_text("1. Company Overview", style="B", size=14)
        add_text(f"Industry: {report.company.industry}")
        if overview:
            add_text(f"Scale: {overview.get('scale', 'N/A')}")
            add_text(f"Summary:\n{overview.get('summary', 'N/A')}")
        pdf.ln(5)
        
        # Business Info
        add_text("2. Business Information", style="B", size=14)
        if biz:
            add_text("Offerings:", style="B")
            for item in biz.get("offerings", []):
                add_text(f"- {item}")
            add_text("Recent Developments:", style="B")
            for item in biz.get("developments", []):
                add_text(f"- {item}")
            add_text("Expansion Plans:", style="B")
            for item in biz.get("expansion_plans", []):
                add_text(f"- {item}")
        pdf.ln(5)
        
        # Challenges
        add_text("3. Business Challenges", style="B", size=14)
        if chal and "items" in chal:
            for item in chal["items"]:
                add_text(f"- {item.get('challenge')} ({item.get('category')})", style="B")
                add_text(f"Severity: {item.get('severity')}")
                add_text(item.get("reasoning"))
                pdf.ln(2)
        pdf.ln(3)

        # AI Opportunities
        add_text("4. AI Opportunities", style="B", size=14)
        if ai and "items" in ai:
            for item in ai["items"]:
                add_text(f"- {item.get('opportunity')} ({item.get('category')})", style="B")
                add_text(f"Impact: {item.get('impact')} | Effort: {item.get('effort')}")
                add_text(item.get("rationale"))
                pdf.ln(2)
        pdf.ln(3)
        
        # Pitch
        add_text("5. CEO Pitch", style="B", size=14)
        if pitch:
            add_text(pitch.get("content", "N/A"))
            
        return pdf.output(dest='S')
