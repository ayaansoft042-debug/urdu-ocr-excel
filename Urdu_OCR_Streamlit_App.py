import streamlit as st
from PIL import Image
import io
import os
import requests
import pytesseract
import pandas as pd
from pdf2image import convert_from_bytes

# Ensure tessdata dir and Urdu traineddata present
tessdata_dir = os.path.join(os.getcwd(), "tessdata")
os.makedirs(tessdata_dir, exist_ok=True)
urd_path = os.path.join(tessdata_dir, "urd.traineddata")
if not os.path.exists(urd_path):
    try:
        url = "https://github.com/tesseract-ocr/tessdata_best/raw/main/urd.traineddata"
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()
        with open(urd_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as e:
        print("Could not download urd.traineddata:", e)
# tell Tesseract to use local tessdata
os.environ["TESSDATA_PREFIX"] = tessdata_dir

st.set_page_config(page_title="Urdu+English OCR → Excel", layout="wide")
st.title("📄 Urdu + English OCR → Excel (Free Prototype)")

st.markdown(\"\"\"
اپلوڈ کریں: JPG/PNG/PDF
یہ ایپ تصویر یا PDF سے متن نکال کر Excel (.xlsx) میں ڈاؤنلوڈ ہونے کے لیے دیتی ہے۔
اگر آپ کو table-wise columns چاہیے تو بہتر نتائج کے لیے high-resolution (300 DPI) تصاویر دیں۔
\"\"\")

uploaded_file = st.file_uploader("PDF یا تصویر اپلوڈ کریں (jpg, png, pdf)", type=["jpg","jpeg","png","pdf"])

def image_from_upload(uploaded):
    # return list of PIL images (for PDF may be multiple pages)
    data = uploaded.read()
    name = uploaded.name.lower()
    if name.endswith(".pdf"):
        try:
            pages = convert_from_bytes(data, dpi=300)
            return pages
        except Exception as e:
            st.error("PDF to image conversion failed: " + str(e))
            return []
    else:
        try:
            img = Image.open(io.BytesIO(data)).convert("RGB")
            return [img]
        except Exception as e:
            st.error("Image open failed: " + str(e))
            return []

if uploaded_file is not None:
    images = image_from_upload(uploaded_file)
    all_lines = []
    page_no = 0
    for img in images:
        page_no += 1
        st.subheader(f"Page {page_no}")
        st.image(img, use_column_width=True)
        with st.spinner("OCR چل رہا ہے... (ہو سکتا ہے کچھ دیر لگے)"):
            try:
                # try Urdu + English
                txt = pytesseract.image_to_string(img, lang="urd+eng", config='--oem 3 --psm 6')
            except Exception as e:
                # fallback to default language
                txt = pytesseract.image_to_string(img)
            lines = [l.strip() for l in txt.split("\\n") if l.strip()]
            st.write(f"Extracted {len(lines)} lines from page {page_no}")
            if len(lines) > 0:
                st.write(lines[:10])
            all_lines.extend(lines)

    if all_lines:
        df = pd.DataFrame(all_lines, columns=["Extracted"])
        st.subheader("Combined Preview")
        st.dataframe(df.head(200))

        towrite = io.BytesIO()
        df.to_excel(towrite, index=False, engine="xlsxwriter")
        towrite.seek(0)
        st.download_button("📥 Download Excel (.xlsx)", data=towrite, file_name="ocr_output.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("کوئی متن نہیں ملا۔ تصویر واضح ہے؟")