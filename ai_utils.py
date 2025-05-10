from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image
import fitz  # PyMuPDF
import uuid
import os
import pandas as pd

# Use public model instead of private one
processor = DonutProcessor.from_pretrained("microsoft/donut-base")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/donut-base")

def convert_pdf_with_donut(pdf_path):
    """
    Converts bank statement PDF using AI model
    """
    doc = fitz.open(pdf_path)
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    all_tables = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        pixel_values = processor(img, return_tensors="pt").pixel_values
        task_prompt = "<s>"
        decoder_input_ids = processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt").input_ids

        outputs = model.generate(
            pixel_values,
            decoder_input_ids=decoder_input_ids,
            max_new_tokens=512,
            early_stopping=True,
            num_beams=1,
            bad_words_ids=[[processor.tokenizer.unk_token_id]],
            return_dict_in_generate=True,
        )

        sequence = processor.batch_decode(outputs.sequences)[0]
        table_data = processor.tokenizer.post_process(sequence)

        if table_data:
            df = pd.DataFrame(table_data)
            all_tables.append(df)

    if not all_tables:
        return None

    final_df = pd.concat(all_tables, ignore_index=True)
    output_filename = f"{uuid.uuid4()}.xlsx"
    final_df.to_excel(os.path.join("outputs", output_filename), index=False)

    return output_filename
