from fpdf import FPDF
from fpdf.errors import FPDFException

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", "", 11)

pdf.multi_cell(0, 8, text="Hello world", new_x="LMARGIN", new_y="NEXT")
print(f"X after multi_cell: {pdf.get_x()}")
