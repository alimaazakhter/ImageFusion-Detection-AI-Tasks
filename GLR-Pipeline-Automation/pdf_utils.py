import PyPDF2
import pytesseract
import fitz  # PyMuPDF
from PIL import Image
import io


def extract_text_from_pdf(file):
    """
    Extracts text from a PDF file-like object.
    - Uses PyPDF2 for text-based PDFs.
    - Uses OCR (pytesseract + PyMuPDF) for image-based (scanned/photo) PDFs.
    Returns a tuple: (extracted_text, warnings_list)
    Requires Tesseract OCR to be installed on your system.
    """
    text = ""
    warnings = []
    try:
        reader = PyPDF2.PdfReader(file)
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            if page_text.strip():
                text += page_text
            else:
                # OCR fallback for image-based page using PyMuPDF
                try:
                    file.seek(0)
                    pdf_bytes = file.read()
                    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                    page_fitz = doc.load_page(i)
                    pix = page_fitz.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr_text = pytesseract.image_to_string(img)
                    if ocr_text.strip():
                        text += ocr_text
                    else:
                        warnings.append(f"No text extracted from page {i+1} (OCR returned empty).")
                except Exception as ocr_e:
                    warnings.append(f"OCR failed on page {i+1}: {ocr_e}")
    except Exception as e:
        warnings.append(f"Error extracting text from PDF: {e}")
        return "", warnings
    if not text.strip():
        warnings.append("No text could be extracted from the entire PDF.")
    return text.strip(), warnings
