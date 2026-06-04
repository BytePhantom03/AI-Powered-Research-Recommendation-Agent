from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", "", 11)

try:
    pdf.multi_cell(0, 8, txt="[content omitted - encoding issue]")
    print("Placeholder worked!")
except Exception as e:
    print(f"Error: {e}")

pdf.output("test.pdf")
print("Done")
