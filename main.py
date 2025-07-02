import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from PIL import Image
import numpy as np
import easyocr
import io
import pandas as pd
from fpdf import FPDF

from ocr.ocr_utils import parse_extracted
from db.db_utils import init_db, insert_card, list_cards, delete_card, fetch_names

st.set_page_config(layout="wide", page_title="BizCardX")

conn = init_db()

menu = st.sidebar.radio("Menu", ["Home", "Upload & Extract", "Stored Cards", "Delete Card"])

if menu == "Home":
    st.markdown("<h1 style='text-align:center; color:white;'>👋 Welcome to BizCardX</h1>", unsafe_allow_html=True)

    img_path = os.path.join(os.path.dirname(__file__), "..", "ocr", "home", "homepage.jpg")
    img = Image.open(img_path)
    st.image(img, use_container_width=True)

    st.markdown("""
    <div style="text-align:center; color:#FFFAFA; font-size:16px; margin-top:20px;">
        BizCardX helps you effortlessly scan, edit, and manage your business card data.<br><br>
        • Upload card images and extract info using OCR<br>
        • Edit and save details to your database<br>
        • View or delete stored cards whenever you like
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:left; color:#90EE90; font-size:14px; margin-top:40px;">
        👩 <strong>Developed by Anvitha Shetty</strong><br>
        ✉️ <strong>anvithashetty@example.com</strong>
    </div>
    """, unsafe_allow_html=True)

elif menu == "Upload & Extract":
    uploaded = st.file_uploader("Upload Business Card", type=["png", "jpg", "jpeg"])
    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, use_container_width=True)
        reader = easyocr.Reader(['en'], gpu=False)
        raw = reader.readtext(np.array(img), detail=0)
        parsed = parse_extracted(raw)

        st.subheader("Extracted Data")
        for k, v in parsed.items():
            parsed[k] = st.text_input(k, v)

        if st.button("Save"):
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            insert_card(conn, parsed, buf.getvalue())
            st.success("✅ Card saved!")

elif menu == "Stored Cards":
    st.subheader("📋 Stored Business Cards")
    rows = list_cards(conn)
    names = fetch_names(conn)
    selected_name = st.selectbox("Filter by Name", ["-- All --"] + names)

    filtered = rows if selected_name == "-- All --" else [r for r in rows if r["Name"] == selected_name]

    if filtered:
        df = pd.DataFrame(filtered).drop(columns=["Image"])
        st.dataframe(df)

        # CSV export
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", data=csv_bytes, file_name="cards.csv", mime="text/csv")

        # PDF export
        def make_pdf(cards_list):
            pdf = FPDF()
            pdf.set_font("Arial", size=12)
            for card in cards_list:
                pdf.add_page()
                for key in ["Name", "Designation", "Company", "Contact", "Email", "Website", "Address", "Pincode"]:
                    pdf.multi_cell(0, 8, f"{key}: {card.get(key,'')}")
                pdf.ln()
            return pdf.output(dest="S").encode("latin-1")

        pdf_bytes = make_pdf(filtered)
        st.download_button("📥 Download PDF", data=pdf_bytes, file_name="cards.pdf", mime="application/pdf")

    else:
        st.warning("No cards found.")

elif menu == "Delete Card":
    st.subheader("🗑️ Delete Stored Card")
    names = fetch_names(conn)
    selected_name = st.selectbox("Select Name", [""] + names)
    designation = st.text_input("Designation")

    if st.button("Delete"):
        if selected_name and designation:
            deleted = delete_card(conn, selected_name, designation)
            if deleted:
                st.success(f"Deleted '{selected_name}' — '{designation}'")
            else:
                st.error(f"No matching card found for '{selected_name}' + '{designation}'")
        else:
            st.warning("Please provide both Name and Designation.")
