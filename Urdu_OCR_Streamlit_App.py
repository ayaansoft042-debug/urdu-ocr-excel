import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import io

st.set_page_config(page_title="Urdu Image to Excel OCR", layout="centered")

st.title("📄 Urdu Image to Excel OCR Tool")

uploaded_file = st.file_uploader("تصویر اپ لوڈ کریں", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    with st.spinner("📖 ٹیکسٹ پڑھا جا رہا ہے..."):
        extracted_text = pytesseract.image_to_string(image, lang="urd+eng")

    st.subheader("📜 Extracted Text")
    st.text(extracted_text)

    if extracted_text.strip():
        # Save to Excel
        df = pd.DataFrame([extracted_text.split("\n")]).T
        df.columns = ["Extracted Text"]

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="OCR_Data")

        st.download_button(
            label="📥 Download as Excel",
            data=output.getvalue(),
            file_name="ocr_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
