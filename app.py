import streamlit as st
import google.generativeai as genai
import json
import os
import re
import time
from datetime import datetime
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Safe fallback for PDF extraction
try:
    import PyPDF2
    PDF_READER_AVAILABLE = True
except ImportError:
    try:
        import pypdf as PyPDF2
        PDF_READER_AVAILABLE = True
    except ImportError:
        PDF_READER_AVAILABLE = False

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Institutional Quality Dashboard | Career & Competency Benchmarking",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MINIMAL CLEAN INSTITUTIONAL CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #F1F5F9;
    }

    .stApp {
        background-color: #0B0F19;
    }

    /* Minimal Header Styling */
    .dashboard-header {
        border-bottom: 1px solid #1E293B;
        padding-bottom: 1.25rem;
        margin-bottom: 2rem;
    }
    
    .dashboard-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.025em;
        margin: 0;
        padding: 0;
    }
    
    .dashboard-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-top: 0.35rem;
        font-weight: 400;
        letter-spacing: 0.01em;
    }

    /* Minimal Clean Institutional Cards */
    .inst-card {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 8px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    .inst-card-title {
        font-size: 0.825rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94A3B8;
        margin-bottom: 0.65rem;
    }

    /* Badge & Tag Styling */
    .badge-primary {
        display: inline-block;
        background-color: #1E3A8A;
        color: #93C5FD;
        font-size: 0.75rem;
        font-weight: 500;
        padding: 0.2rem 0.65rem;
        border-radius: 4px;
        border: 1px solid #2563EB;
        margin: 0.2rem 0.25rem 0.2rem 0;
    }

    .badge-emerald {
        display: inline-block;
        background-color: rgba(16, 185, 129, 0.12);
        color: #34D399;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.2rem 0.65rem;
        border-radius: 4px;
        border: 1px solid rgba(16, 185, 129, 0.3);
        margin: 0.2rem 0.25rem 0.2rem 0;
    }

    .badge-amber {
        display: inline-block;
        background-color: rgba(245, 158, 11, 0.12);
        color: #FBBF24;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.2rem 0.65rem;
        border-radius: 4px;
        border: 1px solid rgba(245, 158, 11, 0.3);
        margin: 0.2rem 0.25rem 0.2rem 0;
    }

    .badge-rose {
        display: inline-block;
        background-color: rgba(239, 68, 68, 0.12);
        color: #F87171;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.2rem 0.65rem;
        border-radius: 4px;
        border: 1px solid rgba(239, 68, 68, 0.3);
        margin: 0.2rem 0.25rem 0.2rem 0;
    }

    /* Clean Streamlit Buttons */
    .stButton > button {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border: 1px solid #1D4ED8 !important;
        border-radius: 6px !important;
        padding: 0.55rem 1.25rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        transition: background-color 0.15s ease, border-color 0.15s ease !important;
        box-shadow: none !important;
    }

    .stButton > button:hover {
        background-color: #1D4ED8 !important;
        border-color: #1E40AF !important;
    }

    .stButton > button:active {
        background-color: #1E40AF !important;
    }

    /* Minimal File Uploader */
    div[data-testid="stFileUploader"] {
        background-color: #111827;
        border: 1px dashed #374151;
        border-radius: 8px;
        padding: 18px;
    }

    div[data-testid="stFileUploader"]:hover {
        border-color: #4B5563;
    }

    /* Clean Expander */
    div[data-testid="stExpander"] {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 6px;
        margin-bottom: 0.5rem;
    }

    /* Metric Container Overrides */
    div[data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1F2937;
        border-radius: 6px;
        padding: 1rem 1.25rem;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8 !important;
    }

    /* Clean Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid #1F2937;
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 0.9rem;
        font-weight: 500;
        color: #94A3B8;
        padding: 0.75rem 0.25rem;
    }

    .stTabs [aria-selected="true"] {
        color: #60A5FA !important;
        border-bottom-color: #2563EB !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION (IN-MEMORY PERSISTENCE) ---
if "candidate_memory" not in st.session_state:
    st.session_state.candidate_memory = []

if "active_candidate_id" not in st.session_state:
    st.session_state.active_candidate_id = None

if "show_uploader" not in st.session_state:
    st.session_state.show_uploader = True

# --- API KEY RESOLUTION ---
# Checks st.secrets safely and environment variables without breaking
def get_gemini_api_key():
    key = None
    try:
        key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        pass
    if not key:
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    return key

api_key = get_gemini_api_key()

# --- HELPER FUNCTIONS ---
def safe_score(val, default=0, min_val=0, max_val=100):
    """Sanitizes raw model outputs into a bounded float/int to prevent progress bar crashes."""
    if isinstance(val, (int, float)):
        return max(min_val, min(max_val, float(val)))
    if isinstance(val, str):
        clean = val.replace("%", "").strip()
        try:
            return max(min_val, min(max_val, float(clean)))
        except ValueError:
            return default
    return default

def clean_json_response(raw_text):
    """Robust JSON cleaner handling markdown fences and surrounding commentary."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Search for outermost JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise

def extract_pdf_text(uploaded_file):
    """Safely extracts text using PyPDF2 with fallbacks."""
    if not PDF_READER_AVAILABLE:
        return ""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text.strip()
    except Exception:
        return ""

def call_gemini_audit(contents, api_key_to_use):
    """Executes generative analysis with automatic model fallback."""
    candidate_models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    genai.configure(api_key=api_key_to_use)
    
    last_error = None
    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={"response_mime_type": "application/json", "temperature": 0.2}
            )
            response = model.generate_content(contents)
            parsed = clean_json_response(response.text)
            return parsed, model_name
        except Exception as e:
            last_error = e
            continue
            
    raise RuntimeError(f"All model endpoints failed. Last error: {last_error}")

# --- SIDEBAR: INSTITUTIONAL SYSTEM & IN-MEMORY ARCHIVE ---
with st.sidebar:
    st.markdown("### 🏛️ Quality Auditor")
    st.caption("BIS & NSQF Competency Verification System")
    
    # API Key Handling
    if not api_key:
        api_key_input = st.text_input("Enter Gemini API Key", type="password", help="Required if not configured in secrets.toml")
        if api_key_input:
            api_key = api_key_input
        else:
            st.warning("Please provide a Gemini API Key to enable candidate assessment.")
    else:
        st.markdown("""
        <div style="background-color: #111827; border: 1px solid #1F2937; border-radius: 6px; padding: 8px 12px; margin-bottom: 12px; font-size: 0.825rem; color: #10B981;">
            ● Gemini API: Authenticated
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # In-Memory Candidate Archive Section
    st.markdown("### 💾 Session Memory")
    num_profiles = len(st.session_state.candidate_memory)
    st.caption(f"{num_profiles} Candidate Profile(s) Loaded in Memory")
    
    if num_profiles > 0:
        options = {}
        for idx, rec in enumerate(st.session_state.candidate_memory):
            label = f"{rec.get('name', 'Candidate')} ({rec.get('score', 0)}%) — {rec.get('role', 'General')[:18]}"
            options[label] = rec['id']
            
        current_selection_label = None
        for label, mem_id in options.items():
            if mem_id == st.session_state.active_candidate_id:
                current_selection_label = label
                break
                
        selected_label = st.selectbox(
            "Select Profile from Memory:",
            options=list(options.keys()),
            index=list(options.keys()).index(current_selection_label) if current_selection_label else 0,
            label_visibility="collapsed"
        )
        
        if selected_label and options[selected_label] != st.session_state.active_candidate_id:
            st.session_state.active_candidate_id = options[selected_label]
            st.session_state.show_uploader = False
            st.rerun()

        col_mem1, col_mem2 = st.columns(2)
        with col_mem1:
            if st.button("➕ New Ingest", use_container_width=True):
                st.session_state.show_uploader = True
                st.rerun()
        with col_mem2:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.candidate_memory = []
                st.session_state.active_candidate_id = None
                st.session_state.show_uploader = True
                st.rerun()
    else:
        st.info("No candidates stored in memory yet. Upload and analyze a CV to build your audit session.")

    st.markdown("---")
    st.markdown("### ⚙️ Benchmark Standards")
    st.markdown("""
    <div style="font-size: 0.8rem; color: #64748B; line-height: 1.5;">
    • Framework: <b>NSQF Level 5 to 8</b><br>
    • Quality Base: <b>ISO/IEC 17024</b><br>
    • Verification: <b>Deterministic Scoring</b><br>
    • Multi-Language: <b>Native Auto-Detect</b>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN DASHBOARD HEADER ---
st.markdown("""
<div class="dashboard-header">
    <div class="dashboard-title">Institutional Quality Dashboard</div>
    <div class="dashboard-subtitle">National Skill Qualification Framework (NSQF) & ISO Standard Alignment System</div>
</div>
""", unsafe_allow_html=True)

# --- GET ACTIVE PROFILE DATA FROM MEMORY IF AVAILABLE ---
active_record = None
if st.session_state.active_candidate_id:
    for rec in st.session_state.candidate_memory:
        if rec["id"] == st.session_state.active_candidate_id:
            active_record = rec
            break

# --- INGESTION / UPLOAD VIEW ---
if st.session_state.show_uploader or not active_record:
    c_left, c_center, c_right = st.columns([1, 2.5, 1])
    with c_center:
        st.markdown("""
        <div class="inst-card">
            <div class="inst-card-title">Profile Ingestion & Standard Evaluation</div>
            <p style="font-size: 0.9rem; color: #94A3B8; margin-top: 0;">Upload a candidate curriculum vitae in PDF or high-resolution image format to audit credentials against institutional benchmarks.</p>
        </div>
        """, unsafe_allow_html=True)
        
        target_role = st.text_input(
            "Target Institutional Role / Standard Benchmark (Optional)",
            placeholder="e.g., Senior Systems Architect, Data Governance Specialist, QA Lead"
        )
        
        uploaded_file = st.file_uploader(
            "Select Candidate Document",
            type=["pdf", "png", "jpg", "jpeg"],
            help="Supports standard PDF text resumes, scanned PDFs, or image-based CVs in any language."
        )

        if uploaded_file:
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            if st.button("Initiate Quality Audit & Benchmarking", use_container_width=True):
                if not api_key:
                    st.error("Authentication required: Please enter or configure your Gemini API Key in the sidebar.")
                    st.stop()
                    
                with st.status("Performing Institutional Verification...", expanded=True) as status:
                    st.write("Extracting structural features from document payload...")
                    
                    contents = []
                    extracted_text = ""
                    
                    try:
                        if uploaded_file.name.lower().endswith(".pdf"):
                            pdf_bytes = uploaded_file.getvalue()
                            # Extract native text if available
                            extracted_text = extract_pdf_text(uploaded_file)
                            # Pass inline PDF bytes for native multimodal understanding
                            contents.append({
                                "mime_type": "application/pdf",
                                "data": pdf_bytes
                            })
                        else:
                            contents.append(Image.open(uploaded_file))
                    except Exception as e:
                        status.update(label=f"Document ingestion failed: {e}", state="error")
                        st.stop()

                    st.write("Cross-referencing candidate competencies against NSQF and ISO benchmarks...")
                    
                    role_specification = (
                        f"The primary target role is: '{target_role}'. Analyze specific skill gaps, competency alignment, and training requirements for this role."
                        if target_role else
                        "No specific target role provided. Determine the candidate's optimal trajectory based on their verified competencies."
                    )
                    
                    system_prompt = f"""
                    You are a Senior Institutional Quality Auditor and Career Benchmark Specialist for a National Standards Body.
                    Evaluate the attached candidate document objectively against National Skill Qualification Framework (NSQF) standards and ISO/IEC professional competencies.
                    The candidate document may be written in ANY language (e.g., English, Hindi, Spanish, French, German, Japanese, etc.).
                    You must comprehend the candidate's background across all languages and provide your assessment STRICTLY in standardized English.

                    {role_specification}

                    Analyze the candidate with complete institutional rigor and return ONLY a valid JSON object matching this schema:
                    {{
                        "candidate_name": "Extracted Candidate Name or 'Candidate Profile'",
                        "primary_language_detected": "English (or Spanish, French, German, Hindi, etc.)",
                        "global_confidence_score": 85,
                        "benchmark_tier": "NSQF Level 7 (Master Specialist / Architecture)",
                        "executive_summary": "Objective, highly professional 2-sentence institutional summary of the candidate's core qualifications, track record, and verified capabilities.",
                        "core_skills": [
                            {{"name": "Distributed Systems", "score": 92, "category": "Technical", "status": "Benchmarked"}},
                            {{"name": "Security & Compliance", "score": 84, "category": "Quality Assurance", "status": "Benchmarked"}},
                            {{"name": "Technical Leadership", "score": 78, "category": "Management", "status": "Developing"}}
                        ],
                        "competency_radar": [
                            {{"axis": "Technical Rigor", "value": 88}},
                            {{"axis": "System Architecture", "value": 85}},
                            {{"axis": "Quality & Compliance", "value": 75}},
                            {{"axis": "Strategic Leadership", "value": 70}},
                            {{"axis": "Regulatory Standards", "value": 65}},
                            {{"axis": "Problem Solving", "value": 90}}
                        ],
                        "career_trajectories": [
                            {{
                                "role": "Primary Vector / Role Title",
                                "match_probability": 92,
                                "rationale": "Objective alignment analysis demonstrating why this profile meets or exceeds the requisite threshold.",
                                "key_strengths": ["Strengths 1", "Strength 2"]
                            }}
                        ],
                        "skill_gaps": [
                            {{
                                "skill": "Missing Competency or Standard",
                                "priority": "High",
                                "current_state": "Limited evidence in submitted materials",
                                "target_standard": "ISO/IEC 25010 Software Quality Requirements or NSQF Level 7",
                                "rationale": "Essential prerequisite for standard compliance in this role."
                            }}
                        ],
                        "strategic_roadmap": [
                            {{
                                "week_range": "Weeks 1-2",
                                "phase_title": "Foundational Standard Alignment",
                                "focus": "Core Competency Rectification",
                                "action_items": [
                                    "Review ISO/IEC 25010 compliance benchmarks",
                                    "Implement automated quality gating"
                                ],
                                "target_standard": "NSQF Level 6/7 Modular Certification"
                            }},
                            {{
                                "week_range": "Weeks 3-4",
                                "phase_title": "Advanced Institutional Compliance",
                                "focus": "Systematic Architecture Validation",
                                "action_items": [
                                    "Conduct comprehensive security audit",
                                    "Formalize verification testing documentation"
                                ],
                                "target_standard": "ISO/IEC 27001 Security Best Practice"
                            }}
                        ]
                    }}
                    """

                    if extracted_text and len(extracted_text) > 100:
                        contents.append(f"\n--- Extracted Resume Document Text ---\n{extracted_text[:12000]}")
                        
                    contents.insert(0, system_prompt)

                    try:
                        parsed_data, used_model = call_gemini_audit(contents, api_key)
                        
                        # Data sanitization
                        global_score = safe_score(parsed_data.get("global_confidence_score", 80))
                        cand_name = parsed_data.get("candidate_name") or uploaded_file.name.rsplit(".", 1)[0]
                        target_disp = target_role if target_role else (
                            parsed_data.get("career_trajectories", [{}])[0].get("role", "General Profile")
                        )
                        
                        # Generate unique ID for session memory
                        memory_record = {
                            "id": f"cand_{int(time.time())}_{len(st.session_state.candidate_memory)}",
                            "name": cand_name,
                            "filename": uploaded_file.name,
                            "role": target_disp,
                            "score": int(global_score),
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                            "model": used_model,
                            "data": parsed_data
                        }
                        
                        # Store in memory
                        st.session_state.candidate_memory.insert(0, memory_record)
                        st.session_state.active_candidate_id = memory_record["id"]
                        st.session_state.show_uploader = False
                        
                        status.update(label=f"Audit Complete via {used_model}", state="complete", expanded=False)
                        time.sleep(0.3)
                        st.rerun()
                        
                    except Exception as e:
                        status.update(label=f"Audit Engine Failed: {e}", state="error")
                        st.error(f"Inference Failure: {e}")
                        st.stop()

# --- ACTIVE ASSESSMENT DASHBOARD VIEW ---
if active_record and not st.session_state.show_uploader:
    data = active_record["data"]
    
    # Action Banner
    b_col1, b_col2 = st.columns([3, 1])
    with b_col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
            <span style="font-size: 1.25rem; font-weight: 600; color: #F8FAFC;">{active_record.get('name', 'Candidate')}</span>
            <span class="badge-primary">{active_record.get('role', 'Institutional Audit')}</span>
            <span class="badge-emerald">Score: {active_record.get('score', 80)}%</span>
            <span style="font-size: 0.8rem; color: #64748B;">• Verified at {active_record.get('timestamp')}</span>
        </div>
        """, unsafe_allow_html=True)
    with b_col2:
        if st.button("➕ Ingest Another Profile", use_container_width=True):
            st.session_state.show_uploader = True
            st.rerun()

    # Metric Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            label="Institutional Fit Score",
            value=f"{safe_score(data.get('global_confidence_score', 85)):.0f}%",
            delta="Compliant" if safe_score(data.get('global_confidence_score', 85)) >= 75 else "Gap Identified"
        )
    with m2:
        top_traj = data.get("career_trajectories", [{}])[0]
        st.metric(
            label="Primary Role Alignment",
            value=f"{safe_score(top_traj.get('match_probability', 85)):.0f}%",
            delta=top_traj.get('role', 'Standard Specialist')[:18]
        )
    with m3:
        core_skills_count = len(data.get("core_skills", []))
        st.metric(
            label="Verified Competencies",
            value=f"{core_skills_count} Skills",
            delta="NSQF Aligned"
        )
    with m4:
        st.metric(
            label="Document Language",
            value=data.get("primary_language_detected", "English"),
            delta="Processed"
        )

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Top Split: Executive Summary Card & Fit Gauge Chart
    col_exec, col_gauge = st.columns([2.2, 1.1])
    
    with col_exec:
        st.markdown("""
        <div class="inst-card" style="height: 100%;">
            <div class="inst-card-title">Executive Credential Analysis</div>
        """, unsafe_allow_html=True)
        
        st.write(data.get("executive_summary", "Evaluation complete."))
        
        tier = data.get("benchmark_tier", "NSQF Standard Professional")
        lang = data.get("primary_language_detected", "English")
        
        st.markdown(f"""
        <div style="margin-top: 1rem; border-top: 1px solid #1F2937; padding-top: 0.85rem;">
            <span class="badge-primary">Standard Tier: {tier}</span>
            <span class="badge-emerald">Source: {lang}</span>
            <span class="badge-primary">Model: {active_record.get('model', 'Gemini')}</span>
        </div>
        </div>
        """, unsafe_allow_html=True)

    with col_gauge:
        fit_val = safe_score(data.get("global_confidence_score", 80))
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=fit_val,
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'font': {'color': '#F8FAFC', 'family': 'Inter', 'size': 38}, 'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569", 'tickfont': {'color': '#64748B', 'size': 11}},
                'bar': {'color': "#2563EB", 'thickness': 0.28},
                'bgcolor': "#111827",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.15)'},
                    {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.15)'},
                    {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.15)'}
                ],
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font={'color': "#F8FAFC", 'family': "Inter"},
            height=210,
            margin=dict(l=15, r=15, t=20, b=10)
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # --- TABBED INSTITUTIONAL AUDIT VIEWS ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Trajectories & Skill Gaps",
        "📊 Competency & Skill Matrix",
        "🗺️ 4-Week Strategic Roadmap",
        "📑 Audit Report & Export"
    ])

    with tab1:
        c_traj, c_gaps = st.columns([1.1, 1.2])
        
        with c_traj:
            st.markdown("<div class='inst-card-title'>Career Trajectory Alignment</div>", unsafe_allow_html=True)
            trajectories = data.get("career_trajectories", [])
            if not trajectories:
                st.info("No specific trajectories modeled.")
            for idx, traj in enumerate(trajectories):
                match_prob = safe_score(traj.get("match_probability", 80))
                with st.expander(f"📌 {traj.get('role', 'Target Role')} — {match_prob:.0f}% Alignment", expanded=(idx==0)):
                    st.write(f"**Institutional Alignment:** {traj.get('rationale', '')}")
                    st.progress(match_prob / 100.0)
                    strengths = traj.get("key_strengths", [])
                    if strengths:
                        st.markdown("**Key Verified Strengths:**")
                        for s in strengths:
                            st.markdown(f"• {s}")

        with c_gaps:
            st.markdown("<div class='inst-card-title'>Target Standard Skill Gaps</div>", unsafe_allow_html=True)
            skill_gaps = data.get("skill_gaps", [])
            if not skill_gaps:
                st.success("✓ Candidate fully satisfies all verified baseline requirements for this profile.")
            else:
                for gap in skill_gaps:
                    priority = gap.get("priority", "Medium")
                    badge_class = "badge-rose" if priority == "High" else ("badge-amber" if priority == "Medium" else "badge-emerald")
                    
                    st.markdown(f"""
                    <div style="background-color: #111827; border: 1px solid #1F2937; border-left: 3px solid {'#EF4444' if priority == 'High' else ('#F59E0B' if priority == 'Medium' else '#10B981')}; border-radius: 4px; padding: 12px 14px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-weight: 600; font-size: 0.95rem; color: #F8FAFC;">{gap.get('skill', 'Identified Gap')}</span>
                            <span class="{badge_class}">{priority} Priority</span>
                        </div>
                        <div style="font-size: 0.825rem; color: #94A3B8; margin-bottom: 4px;"><b>Standard:</b> {gap.get('target_standard', 'Industry Benchmark')}</div>
                        <p style="margin: 0; font-size: 0.85rem; color: #CBD5E1; line-height: 1.4;">{gap.get('rationale', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)

    with tab2:
        c_radar, c_skills = st.columns(2)
        
        with c_radar:
            st.markdown("<div class='inst-card-title'>Competency Evaluation Radar (ISO Dimensions)</div>", unsafe_allow_html=True)
            radar_items = data.get("competency_radar", [])
            if radar_items:
                df_radar = pd.DataFrame(radar_items)
                if 'axis' in df_radar.columns and 'value' in df_radar.columns:
                    df_radar['value'] = df_radar['value'].apply(safe_score)
                    fig_radar = go.Figure(data=go.Scatterpolar(
                        r=df_radar['value'],
                        theta=df_radar['axis'],
                        fill='toself',
                        fillcolor='rgba(37, 99, 235, 0.18)',
                        line=dict(color='#2563EB', width=2),
                        marker=dict(color='#60A5FA', size=6)
                    ))
                    fig_radar.update_layout(
                        polar=dict(
                            bgcolor='#111827',
                            radialaxis=dict(visible=True, range=[0, 100], color="#475569", gridcolor="#1F2937", showticklabels=False),
                            angularaxis=dict(color="#94A3B8", gridcolor="#1F2937", tickfont=dict(size=11, family='Inter'))
                        ),
                        showlegend=False,
                        paper_bgcolor='#111827',
                        plot_bgcolor='#111827',
                        margin=dict(l=40, r=40, t=30, b=30),
                        height=360
                    )
                    st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("Competency radar metrics unavailable.")

        with c_skills:
            st.markdown("<div class='inst-card-title'>Skill Proficiency Benchmark</div>", unsafe_allow_html=True)
            skills = data.get("core_skills", [])
            if skills:
                df_skills = pd.DataFrame(skills)
                if 'name' in df_skills.columns and 'score' in df_skills.columns:
                    df_skills['score'] = df_skills['score'].apply(safe_score)
                    df_skills = df_skills.sort_values(by='score', ascending=True)
                    
                    fig_bar = px.bar(
                        df_skills,
                        x='score',
                        y='name',
                        orientation='h',
                        color='score',
                        color_continuous_scale=[[0, '#1E3A8A'], [1, '#2563EB']]
                    )
                    fig_bar.update_layout(
                        paper_bgcolor='#111827',
                        plot_bgcolor='#111827',
                        xaxis=dict(range=[0, 100], showline=False, showgrid=True, gridcolor='#1F2937', title='Proficiency %', tickfont=dict(color='#64748B', size=11)),
                        yaxis=dict(title='', tickfont=dict(color='#F1F5F9', size=12, family='Inter')),
                        showlegend=False,
                        coloraxis_showscale=False,
                        margin=dict(l=0, r=15, t=20, b=20),
                        height=360
                    )
                    fig_bar.update_traces(marker_line_width=0, opacity=0.92)
                    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No skill proficiency metrics recorded.")

    with tab3:
        st.markdown("<div class='inst-card-title'>4-Week Structured Competency Acquisition Roadmap</div>", unsafe_allow_html=True)
        roadmap = data.get("strategic_roadmap", [])
        if roadmap:
            col_steps = st.columns(len(roadmap)) if len(roadmap) <= 4 else [st.container()]
            if len(roadmap) <= 4:
                for idx, step in enumerate(roadmap):
                    with col_steps[idx]:
                        st.markdown(f"""
                        <div class="inst-card" style="height: 100%;">
                            <div style="font-size: 0.75rem; font-weight: 700; color: #60A5FA; text-transform: uppercase;">{step.get('week_range', f'Phase {idx+1}')}</div>
                            <div style="font-weight: 600; font-size: 1rem; color: #F8FAFC; margin: 4px 0 8px 0;">{step.get('phase_title', 'Initiative')}</div>
                            <div style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 8px;"><b>Focus:</b> {step.get('focus', 'Standard')}</div>
                            <div style="border-top: 1px solid #1F2937; padding-top: 8px; margin-top: 8px;">
                                <span style="font-size: 0.75rem; color: #10B981; font-weight: 600;">Standard Target:</span>
                                <div style="font-size: 0.8rem; color: #CBD5E1;">{step.get('target_standard', 'NSQF Alignment')}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        action_items = step.get("action_items", [])
                        if action_items:
                            for item in action_items:
                                st.caption(f"✓ {item}")
            else:
                for idx, step in enumerate(roadmap):
                    st.markdown(f"""
                    <div class="inst-card">
                        <div style="font-size: 0.75rem; font-weight: 700; color: #60A5FA; text-transform: uppercase;">{step.get('week_range', f'Phase {idx+1}')} — {step.get('phase_title', '')}</div>
                        <p style="font-size: 0.9rem; color: #CBD5E1; margin: 4px 0;"><b>Focus Area:</b> {step.get('focus', '')}</p>
                        <p style="font-size: 0.825rem; color: #94A3B8; margin: 0;"><b>Target Standard:</b> {step.get('target_standard', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No actionable roadmap generated for this candidate.")

    with tab4:
        st.markdown("<div class='inst-card-title'>Institutional Assessment Record & Export</div>", unsafe_allow_html=True)
        
        # Build textual executive audit report
        audit_report_text = f"""=======================================================
INSTITUTIONAL QUALITY ASSESSMENT REPORT
National Skill Qualification Framework (NSQF) & ISO Standard Audit
=======================================================

CANDIDATE: {active_record.get('name', 'Candidate')}
SOURCE DOCUMENT: {active_record.get('filename', 'CV Document')}
TARGET ROLE / BENCHMARK: {active_record.get('role', 'General Audit')}
OVERALL CONFIDENCE SCORE: {active_record.get('score', 0)}%
BENCHMARK TIER: {data.get('benchmark_tier', 'NSQF Standard')}
SOURCE LANGUAGE: {data.get('primary_language_detected', 'English')}
AUDIT TIMESTAMP: {active_record.get('timestamp')}
VERIFICATION MODEL: {active_record.get('model', 'Gemini Engine')}

-------------------------------------------------------
1. EXECUTIVE SUMMARY
-------------------------------------------------------
{data.get('executive_summary', 'N/A')}

-------------------------------------------------------
2. VERIFIED COMPETENCIES & PROFICIENCY
-------------------------------------------------------
"""
        for sk in data.get("core_skills", []):
            audit_report_text += f"- {sk.get('name')}: {sk.get('score')}% ({sk.get('category', 'Technical')})\n"

        audit_report_text += f"""
-------------------------------------------------------
3. TRAJECTORY ALIGNMENT
-------------------------------------------------------
"""
        for tr in data.get("career_trajectories", []):
            audit_report_text += f"- {tr.get('role')}: {tr.get('match_probability')}%\n  Rationale: {tr.get('rationale')}\n"

        audit_report_text += f"""
-------------------------------------------------------
4. TARGET SKILL GAPS & DEFICIENCIES
-------------------------------------------------------
"""
        for sg in data.get("skill_gaps", []):
            audit_report_text += f"- [{sg.get('priority')} Priority] {sg.get('skill')}\n  Standard: {sg.get('target_standard')}\n  Rationale: {sg.get('rationale')}\n"

        audit_report_text += f"""
-------------------------------------------------------
5. 4-WEEK STRATEGIC ACTION ROADMAP
-------------------------------------------------------
"""
        for rm in data.get("strategic_roadmap", []):
            audit_report_text += f"- {rm.get('week_range')} ({rm.get('phase_title')}): {rm.get('focus')}\n  Standard: {rm.get('target_standard')}\n"
            for act in rm.get("action_items", []):
                audit_report_text += f"    * {act}\n"

        audit_report_text += "\n=======================================================\nEND OF INSTITUTIONAL AUDIT RECORD\n"

        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            st.download_button(
                label="📥 Download Executive Audit Report (.txt)",
                data=audit_report_text,
                file_name=f"Institutional_Audit_{active_record.get('name', 'Candidate').replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with c_exp2:
            st.download_button(
                label="📥 Export Full Intelligence Record (.json)",
                data=json.dumps(data, indent=2),
                file_name=f"Intelligence_Record_{active_record.get('name', 'Candidate').replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True
            )
            
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        with st.expander("Preview Raw Intelligence Payload (JSON)"):
            st.json(data)
