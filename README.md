# 🏛️ Institutional Quality Dashboard (Project Path-Finder)

An AI-powered institutional intelligence dashboard designed for credential verification, skill gap diagnosis, and NSQF / ISO/IEC standards alignment. It acts as an **Institutional Quality Auditor** using Google Gemini to parse resumes, benchmark competencies against National Skill Qualification Framework (NSQF) levels and ISO/IEC 17024 industry standards, and generate actionable strategic roadmaps.

Live Application: [Institutional Quality Dashboard on Streamlit](https://institutional-quality-dashboard.streamlit.app/)

---

## 🌟 Key Features

- **Minimal Institutional UI**: Executive dark-slate aesthetic with BIS Cobalt Blue accents, clean typographic hierarchy, and responsive layout.
- **In-Memory Session Archive ("Candidate Memory")**: Retains all evaluated profiles in memory during the active session. Switch between past candidate audits instantly without re-running API calls or consuming extra tokens.
- **Multilingual Document Parsing**: Native extraction supporting PDF, PNG, JPG, and JPEG across any language (English, Spanish, French, German, Hindi, Japanese, etc.), standardizing evaluations into English.
- **Competency Benchmarking**:
  - **Global Fit Score Gauge**: Deterministic compliance indicator with institutional threshold bands.
  - **Competency Radar Matrix**: 6-axis institutional evaluation (Technical Rigor, System Architecture, Quality Assurance, Regulatory Compliance, Strategic Leadership, Problem Solving).
  - **Proficiency Index**: Horizontal proficiency benchmark sorted by capability level.
- **Target Role Skill Gap Analysis**: Detailed breakdown comparing candidate credentials against ISO/IEC & NSQF benchmarks with prioritized gap severity badges.
- **4-Week Strategic Action Roadmap**: Phased milestones with specific action items and target certifications.
- **Export & Reporting**: Instant download of executive assessment reports (`.txt`) and complete audit payloads (`.json`).
- **Resilient Inference Engine**: Automatic fallback across `gemini-1.5-flash`, `gemini-2.0-flash`, and `gemini-1.5-pro` with robust JSON sanitization.

---

## 🚀 Running Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/cozyaar/Institutional-Quality-Dashboard.git
   cd Institutional-Quality-Dashboard
   ```

2. **Create and activate a virtual environment (optional):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Gemini API Key:**
   Create `.streamlit/secrets.toml`:
   ```toml
   GEMINI_API_KEY = "your-gemini-api-key-here"
   ```
   *(Alternatively, you can set the `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variable, or enter it securely via the sidebar).*

5. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

---

## ☁️ Deployment on Streamlit Community Cloud

1. Push your repository to GitHub.
2. Link the repository on [Streamlit Community Cloud](https://share.streamlit.io).
3. In the app settings on Streamlit Cloud, navigate to **Secrets** and add:
   ```toml
   GEMINI_API_KEY = "your-api-key"
   ```
4. Deploy! The app will automatically authenticate and begin serving audits.
