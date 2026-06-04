from fpdf import FPDF
from fpdf.errors import FPDFException

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", "", 11)

pdf.set_x(200) # Move X very close to right margin (page width is 210)
try:
    pdf.multi_cell(0, 8, txt="Hello world")
    print("Worked")
except FPDFException as e:
    print(f"Failed: {e}")
