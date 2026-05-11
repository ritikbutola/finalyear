from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

c = canvas.Canvas("test_with_text.pdf", pagesize=letter)
c.drawString(100, 750, "Test PDF Document")
c.drawString(100, 730, "This is a sample PDF with extractable text.")
c.drawString(100, 710, "It can be used to test the RAG chatbot upload functionality.")
c.save()
print("Created test_with_text.pdf")
