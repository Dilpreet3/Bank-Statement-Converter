import pdfplumber
import pandas as pd
import pytesseract
from PIL import Image
import fitz
import uuid
import os
from ai_utils import convert_pdf_with_donut

def convert_pdf_to_excel(pdf_path):
    data = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    data.extend(table)

        df = pd.DataFrame(data[1:], columns=data[0]) if data else pd.DataFrame()

        if df.empty:
            # Try AI-based conversion
            output_filename = convert_pdf_with_donut(pdf_path)
            if output_filename:
                return output_filename
            # If AI fails, fall back to OCR
            raw_text = extract_text_from_pdf(pdf_path)
            lines = raw_text.splitlines()
            filtered = [line.split() for line in lines if line.strip()]
            df = pd.DataFrame(filtered)

        output_filename = f"{uuid.uuid4()}.xlsx"
        df.to_excel(os.path.join("outputs", output_filename), index=False)
        return output_filename

    except Exception as e:
        print("Conversion error:", e)
        return None

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_text = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        if not text.strip():
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img)
        all_text.append(text)
    return "\n".join(all_text)
