# 🧭 Project Path-Finder

Project Path-Finder is a complete Python Streamlit web application designed for the BIS Hybrid Coding Challenge. It acts as an **Institutional Quality Dashboard** that uses AI (Google Gemini 1.5 Flash) to parse resumes, analyze skills against National Skill Qualification Framework (NSQF) levels and ISO/IEC industry standards, and generate actionable roadmaps.

## 🌟 Features
- **Professional Dashboard UI**: Styled with professional "BIS Blue" (`#003366`) colors and responsive components.
- **AI Engine Integration**: Leverages `google-generativeai` (Gemini 1.5 Flash) acting as a BIS Quality Auditor.
- **Resume Extraction**: Extracts text locally from PDF uploads using `PyPDF2`.
- **Match Score**: Analyzes and outputs a matching score with a visual progress bar.
- **Skill Gap Table**: Presents current skills versus IS/NSQF industry standards.
- **4-Week Roadmap**: Recommends BIS-recognized standards and specific, actionable micro-learning chunks.
- **Downloadable Reports**: Exports the fully formed recommendation as a `.txt` file.

## 🚀 How to Run Locally

1. Setup a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows use: venv\Scripts\activate
   # On macOS/Linux use: source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

4. Usage:
   - Provide your **Google Gemini API Key** in the sidebar.
   - Upload a target **PDF Resume**.
   - Input your **Target Career Goal**.
   - Click to Analyze and view your BIS-Aligned Quality Check!

## ☁️ To visit Streamlit

Streamlit Community Cloud is an easy and free way to deploy your Streamlit apps natively.

**Step-by-Step Deployment:**

1. **Visit streamlit link**: 
   https://institutional-quality-dashboard.streamlit.app/
