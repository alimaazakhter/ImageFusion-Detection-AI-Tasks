# 📝 GLR Pipeline: Automated Insurance Template Filler

Automate insurance template filling using photo reports and LLMs via a simple, professional Streamlit interface.

---

## 🚀 Features
- Upload an insurance template in `.docx` format
- Upload one or more photo reports in `.pdf` format
- Extracts text from photo reports
- Uses OpenRouter LLM APIs (GPT-3.5 Turbo, DeepSeek, etc.) to interpret and extract key-value pairs
- Fills the insurance template with extracted data
- Download the completed, filled-in `.docx` document
- Modern, user-friendly UI with error handling and progress feedback

---

## 🔄 How It Works
1. **Upload** your insurance template and photo report PDFs
2. **Extract** text from PDFs
3. **Parse** key-value pairs using an LLM via OpenRouter
4. **Fill** the DOCX template with the extracted data
5. **Download** your completed document

---

## 🛠️ Setup Instructions

1. **Clone the repository** (or download the code):
   ```bash
   git clone <your-repo-url>
   cd Task_3_GLRAutomation
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get an OpenRouter API Key:**
   - Sign up at [OpenRouter](https://openrouter.ai/)
   - Go to [API Keys](https://openrouter.ai/keys) and create a new key

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

---

## 📋 Usage Instructions
1. Open the app in your browser (usually at [http://localhost:8501](http://localhost:8501))
2. Upload your `.docx` insurance template
3. Upload one or more `.pdf` photo reports
4. Enter your OpenRouter API key
5. Select your preferred LLM model (e.g., GPT-3.5 Turbo, DeepSeek)
6. Click **Process and Fill Template**
7. Review the extracted key-value pairs
8. Download your filled-in DOCX template

---

## 🖼️ Example Screenshot
> *(Add your own screenshot here!)*

---

## 👤 Credits
- **Author:** [Your Name]
- **Contact:** [your.email@example.com]

---

## 📄 License
*Add your license here (e.g., MIT, Apache 2.0, etc.)*
