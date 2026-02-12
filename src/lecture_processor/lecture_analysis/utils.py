from pathlib import Path
import fitz


def parse_pdf_by_pages(pdf: str | Path, start: int, end: int):
    doc = fitz.open(pdf)
    for page_num in range(len(doc)):
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        new_doc.close()
    doc.close()
