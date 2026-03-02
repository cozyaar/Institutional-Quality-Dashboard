import streamlit as st
import google.generativeai as genai
import PyPDF2
import json
from PIL import Image

st.set_page_config(
    page_title="Project Path-Finder | Career Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL CSS SYSTEM ---
st.markdown("""
<style>
    :root {
        --primary-color: #0F172A;
        --secondary-color: #334155;
        --accent-color: #2563EB;
        --bg-light: #F8FAFC;
    }
    
    /* Global Styles */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Typography */
    h1 {
        font-family: 'Inter', -apple-system, sans-serif;
        color: var(--primary-color) !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em;
        margin-bottom: 0.25rem !important;
    }
    
    .subtitle-text {
        font-size: 1.125rem;
        color: var(--secondary-color);
        font-weight: 400;
        margin-bottom: 2rem;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 1.5rem;
    }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background-color: var(--bg-light);
        border: 1px solid #E2E8F0;
        border-radius: 0.75rem;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        border-color: var(--accent-color);
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    
    /* Custom Containers */
    .pro-card {
        background-color: var(--bg-light);
        border: 1px solid #E2E8F0;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .pro-card-header {
        font-weight: 600;
        color: var(--primary-color);
        margin-bottom: 0.75rem;
        font-size: 1.1rem;
    }
    
    /* Tags/Badges */
    .skill-badge {
        display: inline-block;
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    /* Progress Bars overrrides */
    .stProgress > div > div > div > div {
        background-color: var(--accent-color);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.title("Project Path-Finder")
st.markdown('<div class="subtitle-text">AI-Powered Skill Gap Analysis & Career Intelligence Platform</div>', unsafe_allow_html=True)

# --- SIDEBAR & FILE UPLOAD ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3095/3095166.png", width=50) # Professional Icon
    st.markdown("### Profile Ingestion")
    uploaded_file = st.file_uploader(
        "Upload candidate resume", 
        type=["pdf", "png", "jpg", "jpeg"],
        help="Supported formats: PDF, PNG, JPG/JPEG"
    )
    
    st.markdown("---")
    st.markdown("### System Status")
    st.markdown("""
    <div style="font-size: 0.9rem; color: #475569;">
    • Core Engine: <b>Operational</b><br>
    • Model: <b>Gemini 2.5 Flash</b><br>
    • Vision API: <b>Enabled</b>
    </div>
    """, unsafe_allow_html=True)

if not uploaded_file:
    st.info("Awaiting file ingestion. Please upload a candidate profile document via the sidebar configuration panel to initiate the AI analysis engine.")
    st.stop()


# --- BACKEND LOGIC ---
if st.button("Initialize Analysis Engine", type="primary", use_container_width=True):
    resume_text = ""
    image_parts = []
    
    try:
        # Document Parsing
        if uploaded_file.name.lower().endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text_chunk = page.extract_text()
                if text_chunk: resume_text += text_chunk + "\n"
        else:
            img = Image.open(uploaded_file)
            image_parts.append(img)
            
    except Exception as e:
        st.error(f"System Error [DOCUMENT_PARSE_FAILED]: {e}")
        st.stop()

    prompt = """
    You are an enterprise Career Intelligence system designed to perform highly analytical, data-driven skill gap assessments.
    Analyze the provided candidate document. Return ONLY valid JSON matching this exact structure:
    {
        "executive_summary": "A highly professional, objective 3-sentence summary of the candidate's trajectory and immediate value proposition.",
        "core_competencies": ["Competency 1", "Competency 2", "Competency 3", "Competency 4"],
        "career_trajectories": [
            {
                "role": "Target Role Name",
                "alignment_score": 90,
                "rationale": "Clear, objective reasoning for this trajectory."
            }
        ],
        "gap_analysis": [
            {
                "competency_area": "Technical/Domain Area",
                "current_proficiency": "Novice/Intermediate/Advanced",
                "target_benchmark": "Industry Standard (e.g., ISO/NSQF)"
            }
        ],
        "strategic_roadmap": [
            {
                "phase": "Q1 Strategic Initiatives",
                "focus": "Core domain",
                "actionables": "Specific tasks",
                "certification_target": "Recommended standard/cert"
            }
        ]
    }
    """

    try:
        api_key_to_use = st.secrets.get("GEMINI_API_KEY")
        if not api_key_to_use:
            st.error("System Error [MISSING_AUTH]: GEMINI_API_KEY secret not found in environment.")
            st.stop()
        genai.configure(api_key=api_key_to_use)
        
        # Updated model from 1.5-flash to 2.5-flash
        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
        
        with st.spinner("Processing document through Gemini 2.5 Flash inference engine..."):
            if image_parts:
                response = model.generate_content([prompt, image_parts[0]])
            else:
                response = model.generate_content(prompt)
                
            data = json.loads(response.text)
            
        # Analysis Complete
        st.markdown("---")
        
        # Executive Layout Grid
        col_exec, col_metrics = st.columns([2, 1])
        
        with col_exec:
            st.markdown("### Executive Summary")
            st.write(data["executive_summary"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Verified Competencies")
            badges_html = "".join([f'<span class="skill-badge">{skill}</span>' for skill in data["core_competencies"]])
            st.markdown(badges_html, unsafe_allow_html=True)

        with col_metrics:
            st.markdown("### Trajectory Alignment")
            for rec in data["career_trajectories"]:
                with st.container():
                    st.metric(label=rec['role'], value=f"{rec['alignment_score']}% Match")
                    st.progress(rec['alignment_score'] / 100)
                    st.caption(rec['rationale'])
                    st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Detailed Intelligence Report")
        
        # Professional Tabs Layout
        tab_gaps, tab_roadmap, tab_export = st.tabs(["Gap Analysis", "Strategic Roadmap", "Data Export"])
        
        with tab_gaps:
            st.markdown("#### Industry Benchmark Assessment")
            st.table(data["gap_analysis"])

        with tab_roadmap:
            st.markdown("#### Competency Acquisition Timeline")
            for step in data["strategic_roadmap"]:
                st.markdown(f"""
                <div class="pro-card">
                    <div class="pro-card-header">{step['phase']} — {step['focus']}</div>
                    <div style="font-size: 0.95rem; color: #334155; margin-bottom: 0.5rem;"><b>Actionables:</b> {step['actionables']}</div>
                    <div style="font-size: 0.9rem; color: #2563EB;"><b>Target Certification:</b> {step['certification_target']}</div>
                </div>
                """, unsafe_allow_html=True)

        with tab_export:
            st.markdown("#### System Integration")
            st.write("Extract intelligence payload for ATS or LMS integration.")
            st.download_button(
                "Export Intelligence Record (JSON)", 
                data=json.dumps(data, indent=4), 
                file_name="candidate_intelligence_record.json", 
                mime="application/json",
                use_container_width=True
            )

    except json.JSONDecodeError:
        st.error("System Error [INVALID_PAYLOAD]: The inference engine returned an unparseable response.")
    except Exception as e:
        error_msg = str(e).lower()
        if "quota" in error_msg or "429" in error_msg:
             st.error("System Error [RATE_LIMIT]: API Quota exceeded. Please try again shortly.")
        elif "404" in error_msg:
             st.error("System Error [MODEL_NOT_FOUND]: The specified inference model is currently unavailable on this API route.")
        else:
             st.error(f"System Error [INTERNAL_FAULT]: {e}")
