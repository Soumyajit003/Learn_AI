# ***this code is taken form to to understand about pydantic, pyPDF2 an pathlib

from pathlib import Path
from typing import List
from PyPDF2 import PdfReader
from pydantic import BaseModel, Field, ValidationError


# Define a Pydantic model for structured PDF data
class PDFPage(BaseModel):
    page_number: int = Field(..., ge=1, description="Page number starting from 1")
    text: str = Field(..., min_length=1, description="Extracted text from the page")


class PDFDocument(BaseModel):
    filename: str
    pages: List[PDFPage]

def read_pdf(file_path: Path) -> PDFDocument:
    """Reads a PDF file and returns structured data validated by Pydantic."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if file_path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    reader = PdfReader(str(file_path))
    pages_data = []

    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text:  # Only include pages with text
            pages_data.append(PDFPage(page_number=idx, text=text.strip()))

    # Validate and return structured document
    return PDFDocument(filename=file_path.name, pages=pages_data)


if __name__ == "__main__":
    try:
        pdf_path = Path("sample.pdf")  # Change to your PDF file path
        document = read_pdf(pdf_path)

        # Print structured output
        print(f"PDF: {document.filename}")
        for page in document.pages:
            print(f"\nPage {page.page_number}:\n{page.text}")

    except (FileNotFoundError, ValueError, ValidationError) as e:
        print(f"Error: {e}")
