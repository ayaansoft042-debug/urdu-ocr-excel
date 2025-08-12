
import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import io

st.set_page_config(page_title="Urdu OCR to Excel", page_icon="📄")

st.title("📄 Urdu + English OCR to Excel Converter")

uploaded_file = st.file_uploader("Upload an image (JPG, PNG) or PDF", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file is not None:
    try:
        # Read image
        image = Image.open(uploaded_file)

        # Perform OCR (Urdu + English)
        custom_oem_psm_config = r'--oem 3 --psm 6 -l urd+eng'
        extracted_text = pytesseract.image_to_string(image, config=custom_oem_psm_config)

        st.subheader("Extracted Text:")
        st.text(extracted_text)

        # Save to Excel
        df = pd.DataFrame({"Extracted Text": extracted_text.split("\n")})
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        st.download_button(
            label="📥 Download as Excel",
            data=excel_buffer,
            file_name="ocr_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error processing file: {e}")

st.caption("Developed by ayaansoft042-debug — Free OCR Tool")
