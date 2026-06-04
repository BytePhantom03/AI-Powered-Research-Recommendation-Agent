from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", "", 11)

pdf.multi_cell(0, 8, txt="Hello world")
print(f"X after multi_cell: {pdf.get_x()}")
