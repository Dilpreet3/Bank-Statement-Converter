import pdfplumber
import pandas as pd
import pytesseract
from PIL import Image
import fitz
import uuid
import os

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
            raw_text = extract_text_from_pdf(pdf_path)
            lines = raw_text.splitlines()
            filtered = [line.split() for line in lines if line.strip()]
            df = pd.DataFrame(filtered)

        output_filename = f"{uuid.uuid4()}.xlsx"
        output_path = os.path.join("outputs", output_filename)
        df.to_excel(output_path, index=False, engine='openpyxl')
        return output_filename
    except Exception as e:
        print("Conversion error:", e)
        return None

def extract_text_from_pdf(pdf_path):
    all_text = []
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        if text.strip():
            all_text.append(text)
        else:
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img)
            all_text.append(text)
    return "\n".join(all_text)
