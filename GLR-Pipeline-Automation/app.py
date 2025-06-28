import streamlit as st
import tempfile
import os
from pdf_utils import extract_text_from_pdf
from llm_utils import extract_key_value_pairs
from docx_utlis import fill_docx_template
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

st.set_page_config(page_title="GLR Insurance Template Filler", page_icon="📝", layout="centered")

# Sidebar
with st.sidebar:
    st.markdown("""
    <h2 style='color:#4f46e5;'>📝 GLR Pipeline</h2>
    <p style='font-size:1.1em;'>Automate <b>insurance template filling</b> using photo reports and LLMs.</p>
    <ul style='font-size:1em; line-height:1.7;'>
      <li>📄 <b>Upload a DOCX template</b></li>
      <li>🖼️ <b>Upload one or more PDF photo reports</b></li>
      <li>🔑 <b>Enter your OpenRouter API key</b></li>
      <li>⬇️ <b>Download the filled template</b></li>
    </ul>
    <hr style='border:1px solid #4f46e5;'>
    <p style='font-size:1em; color:#22c55e;'><b>Made by Alimaaz Akhter</b></p>
    """, unsafe_allow_html=True)

st.title("GLR Insurance Template Filler")
st.markdown("""
This app automates the process of filling insurance templates using photo reports and LLMs. Upload your template and photo reports, and let AI do the rest!
""")

# File uploaders
st.header("1. Upload Files")
template_file = st.file_uploader("Upload Insurance Template (.docx)", type=["docx"], key="template")
pdf_files = st.file_uploader("Upload Photo Reports (.pdf, multiple allowed)", type=["pdf"], accept_multiple_files=True, key="pdfs")

# API key input
api_key = st.text_input("Enter your OpenRouter API Key", type="password")

# Model selection
tt_models = {
    "OpenAI GPT-3.5 Turbo (Recommended)": "openai/gpt-3.5-turbo",
    "DeepSeek Chat": "deepseek/deepseek-chat-v3-0324"
}
model_choice = st.selectbox("Choose LLM Model", list(tt_models.keys()), index=0)
model = tt_models[model_choice]

if st.button("Process and Fill Template"):
    if not template_file or not pdf_files or not api_key:
        st.error("Please upload a DOCX template, at least one PDF, and enter your API key.")
    else:
        with st.spinner("Extracting text from PDF photo reports..."):
            all_text = ""
            for pdf in pdf_files:
                text, warnings = extract_text_from_pdf(pdf)
                if warnings:
                    for w in warnings:
                        st.warning(f"{pdf.name}: {w}")
                if not text:
                    st.warning(f"No text extracted from {pdf.name}. Skipping.")
                else:
                    all_text += f"\n---\n{pdf.name}:\n{text}"
            if not all_text.strip():
                st.error("No text could be extracted from any PDF. Please check your files.")
                st.stop()
        st.success("Text extraction complete.")

        with st.spinner("Extracting key-value pairs using LLM..."):
            key_value_pairs, raw_llm_response = extract_key_value_pairs(all_text, api_key, model=model)
            if not key_value_pairs:
                st.error("LLM could not extract key-value pairs. Please check your API key, model selection, or try again.")
                with st.expander("Show raw LLM response / error details"):
                    st.code(raw_llm_response)
                st.stop()
        st.success("Key-value extraction complete.")

        st.header("2. Extracted Key-Value Pairs")
        st.json(key_value_pairs)

        with st.spinner("Filling DOCX template..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_out:
                success = fill_docx_template(template_file, key_value_pairs, tmp_out.name)
                if not success:
                    st.error("Failed to fill the DOCX template. Please check your template and try again.")
                    st.stop()
                output_path = tmp_out.name
        st.success("Template filled successfully!")

        st.header("3. Download Filled Template")
        with open(output_path, "rb") as f:
            st.download_button(
                label="Download Filled DOCX",
                data=f,
                file_name="Filled_Insurance_Template.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        os.remove(output_path)

st.markdown("---")
st.caption("GLR Pipeline | Powered by Streamlit, OpenRouter, and Python 🐍")
