from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", "", 11)

y1 = pdf.get_y()
pdf.multi_cell(0, 8, txt="Hello world\nSecond line")
print(f"Y before: {y1}, Y after: {pdf.get_y()}, X after: {pdf.get_x()}")
