from fpdf import FPDF
from fpdf.errors import FPDFException

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", "", 11)

pdf.set_x(200) 
pdf.ln(5)
print(f"X after ln(5): {pdf.get_x()}")

try:
    pdf.multi_cell(0, 8, txt="Hello world")
    print("Worked")
except FPDFException as e:
    print(f"Failed: {e}")
