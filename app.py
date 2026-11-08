import streamlit as st
import google.generativeai as genai
import json
import os
import re
import time
import io
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

# --- MODERN SOPHISTICATED INSTITUTIONAL CSS SYSTEM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #F1F5F9;
    }

    .stApp {
        background-color: #080C15;
        background-image: 
            radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.05) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(99, 102, 241, 0.04) 0px, transparent 50%);
    }

    /* Refined Executive Header */
    .dashboard-header {
        border-bottom: 1px solid rgba(56, 189, 248, 0.15);
        padding-bottom: 1.25rem;
        margin-bottom: 2rem;
    }
    
    .dashboard-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.25rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #FFFFFF 30%, #BAE6FD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        padding: 0;
    }
    
    .dashboard-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-top: 0.4rem;
        font-weight: 400;
        letter-spacing: 0.01em;
    }

    /* Rich Elevated Cards */
    .inst-card {
        background: linear-gradient(180deg, #0E1626 0%, #0A101D 100%);
        border: 1px solid rgba(56, 189, 248, 0.14);
        border-radius: 10px;
        padding: 1.35rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.45);
    }

    .inst-card-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #38BDF8;
        margin-bottom: 0.75rem;
    }

    /* KPI Metric Cards */
    .kpi-container {
        background: linear-gradient(180deg, #0E1626 0%, #0A101D 100%);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 10px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.4);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .kpi-label {
        font-size: 0.775rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94A3B8;
        margin-bottom: 0.35rem;
    }

    .kpi-value {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.85rem;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }

    .kpi-subtext {
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.35rem;
    }

    /* Refined Semantic Badges */
    .badge-primary {
        display: inline-block;
        background-color: rgba(37, 99, 235, 0.15);
        color: #60A5FA;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 5px;
        border: 1px solid rgba(96, 165, 250, 0.3);
        margin: 0.2rem 0.25rem 0.2rem 0;
    }

    .badge-emerald {
        display: inline-block;
        background-color: rgba(16, 185, 129, 0.14);
        color: #34D399;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 5px;
        border: 1px solid rgba(52, 211, 153, 0.35);
        margin: 0.2rem 0.25rem 0.2rem 0;
    }

    .badge-amber {
        display: inline-block;
        background-color: rgba(245, 158, 11, 0.14);
        color: #FBBF24;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 5px;
        border: 1px solid rgba(251, 191, 36, 0.35);
        margin: 0.2rem 0.25rem 0.2rem 0;
    }

    .badge-rose {
        display: inline-block;
        background-color: rgba(244, 63, 94, 0.14);
        color: #FB7185;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 5px;
        border: 1px solid rgba(251, 113, 133, 0.35);
        margin: 0.2rem 0.25rem 0.2rem 0;
    }

    .badge-cyan {
        display: inline-block;
        background-color: rgba(6, 182, 212, 0.14);
        color: #22D3EE;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.65rem;
        border-radius: 5px;
        border: 1px solid rgba(34, 211, 238, 0.35);
        margin: 0.2rem 0.25rem 0.2rem 0;
    }

    /* Premium Button Styling */
    .stButton > button {
        background: linear-gradient(180deg, #0284C7 0%, #0369A1 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #38BDF8 !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.4rem !important;
        font-size: 0.925rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em !important;
        box-shadow: 0 2px 10px rgba(2, 132, 199, 0.35) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stButton > button:hover {
        background: linear-gradient(180deg, #0EA5E9 0%, #0284C7 100%) !important;
        border-color: #7DD3FC !important;
        box-shadow: 0 4px 16px rgba(14, 165, 233, 0.5) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Minimal File Uploader */
    div[data-testid="stFileUploader"] {
        background: #0E1626;
        border: 1px dashed rgba(56, 189, 248, 0.35);
        border-radius: 10px;
        padding: 22px;
        transition: border-color 0.2s ease;
    }

    div[data-testid="stFileUploader"]:hover {
        border-color: #38BDF8;
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        background: #0A111E;
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 8px;
        margin-bottom: 0.65rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.75rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.18);
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 0.925rem;
        font-weight: 600;
        color: #94A3B8;
        padding: 0.85rem 0.25rem;
    }

    .stTabs [aria-selected="true"] {
        color: #38BDF8 !important;
        border-bottom-color: #0284C7 !important;
        border-bottom-width: 2px !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #070B13;
        border-right: 1px solid rgba(56, 189, 248, 0.12);
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

def extract_pdf_text(file_bytes):
    """Safely extracts text using PyPDF2 or pypdf with BytesIO stream."""
    if not PDF_READER_AVAILABLE:
        return ""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text.strip()
    except Exception:
        return ""

def get_supported_models(api_key_to_use):
    """Dynamically queries Google API for models that support generateContent."""
    discovered = []
    try:
        genai.configure(api_key=api_key_to_use)
        for m in genai.list_models():
            methods = getattr(m, 'supported_generation_methods', [])
            if 'generateContent' in methods:
                clean = m.name.replace("models/", "")
                discovered.append(clean)
    except Exception:
        pass
        
    preferred_order = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash-exp",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    
    candidates = []
    # 1. Match discovered against preferred order
    for pref in preferred_order:
        for disc in discovered:
            if disc == pref or disc.startswith(pref):
                if disc not in candidates:
                    candidates.append(disc)
                    
    # 2. Add any remaining discovered gemini models
    for disc in discovered:
        if disc not in candidates and "gemini" in disc.lower():
            candidates.append(disc)
            
    # 3. Fallback if discovery returned nothing (e.g. list_models permission restriction)
    for pref in preferred_order:
        if pref not in candidates:
            candidates.append(pref)
            
    return candidates

def call_gemini_audit(contents, api_key_to_use, extracted_text="", system_prompt=""):
    """Executes generative analysis with automatic model discovery and multi-payload fallback."""
    candidate_models = get_supported_models(api_key_to_use)
    genai.configure(api_key=api_key_to_use)
    
    errors = []
    text_fallback_payload = (
        [f"{system_prompt}\n\n=== CANDIDATE RESUME DOCUMENT TEXT ===\n{extracted_text}"]
        if (extracted_text and len(extracted_text.strip()) > 30)
        else None
    )
    
    payloads_to_try = [contents]
    if text_fallback_payload and text_fallback_payload != contents:
        payloads_to_try.append(text_fallback_payload)
        
    for model_name in candidate_models:
        for current_payload in payloads_to_try:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config={"response_mime_type": "application/json", "temperature": 0.2}
                )
                response = model.generate_content(current_payload)
                parsed = clean_json_response(response.text)
                return parsed, model_name
            except Exception as e:
                err_str = str(e)
                # If JSON mode is rejected or unsupported, try plain generation
                if "response_mime_type" in err_str.lower() or "schema" in err_str.lower() or "not supported" in err_str.lower():
                    try:
                        model_plain = genai.GenerativeModel(
                            model_name=model_name,
                            generation_config={"temperature": 0.2}
                        )
                        response = model_plain.generate_content(current_payload)
                        parsed = clean_json_response(response.text)
                        return parsed, model_name
                    except Exception as inner_e:
                        errors.append(f"{model_name}: {inner_e}")
                else:
                    errors.append(f"{model_name}: {err_str}")
                
                # If model is not found (404), skip secondary payload for this model
                if "404" in err_str or "not found" in err_str.lower():
                    break
            
    error_summary = "\n• " + "\n• ".join(errors[:4])
    raise RuntimeError(f"All model endpoints failed:{error_summary}")

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
        <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 6px; padding: 8px 12px; margin-bottom: 12px; font-size: 0.825rem; color: #34D399; font-weight: 500;">
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
    <div style="font-size: 0.8rem; color: #94A3B8; line-height: 1.6;">
    • Framework: <b style="color: #38BDF8;">NSQF Level 5 to 8</b><br>
    • Quality Base: <b style="color: #34D399;">ISO/IEC 17024</b><br>
    • Verification: <b style="color: #FBBF24;">Deterministic Scoring</b><br>
    • Multi-Language: <b style="color: #818CF8;">Native Auto-Detect</b>
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
            <p style="font-size: 0.925rem; color: #CBD5E1; margin-top: 0; line-height: 1.5;">Upload a candidate curriculum vitae in PDF or high-resolution image format to audit credentials against institutional benchmarks.</p>
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
                    
                    file_bytes = uploaded_file.getvalue()
                    extracted_text = ""
                    contents = []
                    
                    try:
                        if uploaded_file.name.lower().endswith(".pdf"):
                            extracted_text = extract_pdf_text(file_bytes)
                            # Format primary payload
                            if extracted_text and len(extracted_text.strip()) > 40:
                                contents = [
                                    {"mime_type": "application/pdf", "data": file_bytes},
                                    f"--- Extracted Document Text ---\n{extracted_text[:14000]}"
                                ]
                            else:
                                contents = [
                                    {"mime_type": "application/pdf", "data": file_bytes}
                                ]
                        else:
                            contents = [Image.open(io.BytesIO(file_bytes))]
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

                    contents.insert(0, system_prompt)

                    try:
                        parsed_data, used_model = call_gemini_audit(
                            contents=contents,
                            api_key_to_use=api_key,
                            extracted_text=extracted_text,
                            system_prompt=system_prompt
                        )
                        
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
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px;">
            <span style="font-family: 'Plus Jakarta Sans'; font-size: 1.35rem; font-weight: 700; color: #F8FAFC;">{active_record.get('name', 'Candidate')}</span>
            <span class="badge-primary">{active_record.get('role', 'Institutional Audit')}</span>
            <span class="badge-emerald">Score: {active_record.get('score', 80)}%</span>
            <span style="font-size: 0.8rem; color: #64748B;">• Verified at {active_record.get('timestamp')}</span>
        </div>
        """, unsafe_allow_html=True)
    with b_col2:
        if st.button("➕ Ingest Another Profile", use_container_width=True):
            st.session_state.show_uploader = True
            st.rerun()

    # Enhanced Top KPI Metric Row with Vibrant Palette
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        fit_val = safe_score(data.get('global_confidence_score', 85))
        delta_label = "✓ Compliant Standard" if fit_val >= 75 else "⚠ Gap Identified"
        delta_color = "#34D399" if fit_val >= 75 else "#FBBF24"
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 3px solid #38BDF8;">
            <div class="kpi-label">Institutional Fit Score</div>
            <div class="kpi-value" style="color: #38BDF8;">{fit_val:.0f}%</div>
            <div class="kpi-subtext" style="color: {delta_color};">{delta_label}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m2:
        top_traj = data.get("career_trajectories", [{}])[0]
        traj_prob = safe_score(top_traj.get('match_probability', 85))
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 3px solid #34D399;">
            <div class="kpi-label">Primary Role Alignment</div>
            <div class="kpi-value" style="color: #34D399;">{traj_prob:.0f}%</div>
            <div class="kpi-subtext" style="color: #94A3B8;">{top_traj.get('role', 'Standard Specialist')[:20]}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m3:
        core_skills_count = len(data.get("core_skills", []))
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 3px solid #FBBF24;">
            <div class="kpi-label">Verified Competencies</div>
            <div class="kpi-value" style="color: #FBBF24;">{core_skills_count}</div>
            <div class="kpi-subtext" style="color: #94A3B8;">NSQF Framework Aligned</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m4:
        st.markdown(f"""
        <div class="kpi-container" style="border-top: 3px solid #818CF8;">
            <div class="kpi-label">Document Language</div>
            <div class="kpi-value" style="color: #818CF8; font-size: 1.5rem;">{data.get('primary_language_detected', 'English')}</div>
            <div class="kpi-subtext" style="color: #94A3B8;">Native AI Translated</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    # Top Split: Executive Summary Card & Fit Gauge Chart
    col_exec, col_gauge = st.columns([2.1, 1.1])
    
    with col_exec:
        st.markdown("""
        <div class="inst-card" style="height: 100%;">
            <div class="inst-card-title">Executive Credential Analysis</div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <p style="font-size: 1.05rem; line-height: 1.65; color: #E2E8F0; margin-bottom: 1.25rem;">
            {data.get('executive_summary', 'Evaluation complete.')}
        </p>
        """, unsafe_allow_html=True)
        
        tier = data.get("benchmark_tier", "NSQF Standard Professional")
        lang = data.get("primary_language_detected", "English")
        
        st.markdown(f"""
        <div style="border-top: 1px solid rgba(148, 163, 184, 0.15); padding-top: 0.85rem;">
            <span class="badge-cyan">Tier: {tier}</span>
            <span class="badge-emerald">Language: {lang}</span>
            <span class="badge-primary">Engine: {active_record.get('model', 'Gemini')}</span>
        </div>
        </div>
        """, unsafe_allow_html=True)

    with col_gauge:
        fit_val = safe_score(data.get("global_confidence_score", 80))
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=fit_val,
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'font': {'color': '#38BDF8', 'family': 'Plus Jakarta Sans', 'size': 42}, 'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#64748B", 'tickfont': {'color': '#94A3B8', 'size': 11}},
                'bar': {'color': "#38BDF8", 'thickness': 0.28},
                'bgcolor': "#0A101D",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(244, 63, 94, 0.18)'},
                    {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.18)'},
                    {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.18)'}
                ],
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor="#0E1626",
            plot_bgcolor="#0E1626",
            font={'color': "#F8FAFC", 'family': "Inter"},
            height=220,
            margin=dict(l=15, r=15, t=20, b=10)
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

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
                            st.markdown(f"• <span style='color: #38BDF8;'>{s}</span>", unsafe_allow_html=True)

        with c_gaps:
            st.markdown("<div class='inst-card-title'>Target Standard Skill Gaps</div>", unsafe_allow_html=True)
            skill_gaps = data.get("skill_gaps", [])
            if not skill_gaps:
                st.success("✓ Candidate fully satisfies all verified baseline requirements for this profile.")
            else:
                for gap in skill_gaps:
                    priority = gap.get("priority", "Medium")
                    badge_class = "badge-rose" if priority == "High" else ("badge-amber" if priority == "Medium" else "badge-emerald")
                    border_color = '#FB7185' if priority == 'High' else ('#FBBF24' if priority == 'Medium' else '#34D399')
                    bg_color = 'rgba(244, 63, 94, 0.08)' if priority == 'High' else ('rgba(245, 158, 11, 0.08)' if priority == 'Medium' else 'rgba(16, 185, 129, 0.08)')
                    
                    st.markdown(f"""
                    <div style="background-color: {bg_color}; border: 1px solid rgba(148, 163, 184, 0.14); border-left: 4px solid {border_color}; border-radius: 6px; padding: 14px 16px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-weight: 700; font-size: 1rem; color: #F8FAFC;">{gap.get('skill', 'Identified Gap')}</span>
                            <span class="{badge_class}">{priority} Priority</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #38BDF8; margin-bottom: 6px;"><b>Target Standard:</b> {gap.get('target_standard', 'Industry Benchmark')}</div>
                        <p style="margin: 0; font-size: 0.885rem; color: #CBD5E1; line-height: 1.45;">{gap.get('rationale', '')}</p>
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
                        fillcolor='rgba(14, 165, 233, 0.22)',
                        line=dict(color='#38BDF8', width=2.5),
                        marker=dict(color='#BAE6FD', size=7)
                    ))
                    fig_radar.update_layout(
                        polar=dict(
                            bgcolor='#0E1626',
                            radialaxis=dict(visible=True, range=[0, 100], color="#64748B", gridcolor="rgba(148, 163, 184, 0.16)", showticklabels=False),
                            angularaxis=dict(color="#E2E8F0", gridcolor="rgba(148, 163, 184, 0.16)", tickfont=dict(size=11, family='Inter'))
                        ),
                        showlegend=False,
                        paper_bgcolor='#0E1626',
                        plot_bgcolor='#0E1626',
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
                        color_continuous_scale=[[0, '#0284C7'], [0.5, '#2563EB'], [1, '#38BDF8']]
                    )
                    fig_bar.update_layout(
                        paper_bgcolor='#0E1626',
                        plot_bgcolor='#0E1626',
                        xaxis=dict(range=[0, 100], showline=False, showgrid=True, gridcolor='rgba(148, 163, 184, 0.12)', title='Proficiency %', tickfont=dict(color='#94A3B8', size=11)),
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
            phase_colors = ["#38BDF8", "#34D399", "#FBBF24", "#818CF8"]
            col_steps = st.columns(len(roadmap)) if len(roadmap) <= 4 else [st.container()]
            if len(roadmap) <= 4:
                for idx, step in enumerate(roadmap):
                    p_color = phase_colors[idx % len(phase_colors)]
                    with col_steps[idx]:
                        st.markdown(f"""
                        <div class="inst-card" style="height: 100%; border-top: 3px solid {p_color};">
                            <div style="font-size: 0.75rem; font-weight: 700; color: {p_color}; text-transform: uppercase;">{step.get('week_range', f'Phase {idx+1}')}</div>
                            <div style="font-weight: 700; font-size: 1.05rem; color: #F8FAFC; margin: 4px 0 8px 0;">{step.get('phase_title', 'Initiative')}</div>
                            <div style="font-size: 0.85rem; color: #94A3B8; margin-bottom: 8px;"><b>Focus:</b> {step.get('focus', 'Standard')}</div>
                            <div style="border-top: 1px solid rgba(148, 163, 184, 0.14); padding-top: 8px; margin-top: 8px;">
                                <span style="font-size: 0.75rem; color: #34D399; font-weight: 700;">Target Standard:</span>
                                <div style="font-size: 0.825rem; color: #CBD5E1; margin-top: 2px;">{step.get('target_standard', 'NSQF Alignment')}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        action_items = step.get("action_items", [])
                        if action_items:
                            for item in action_items:
                                st.markdown(f"<span style='color: {p_color};'>✓</span> <span style='font-size: 0.85rem; color: #CBD5E1;'>{item}</span>", unsafe_allow_html=True)
            else:
                for idx, step in enumerate(roadmap):
                    p_color = phase_colors[idx % len(phase_colors)]
                    st.markdown(f"""
                    <div class="inst-card" style="border-left: 4px solid {p_color};">
                        <div style="font-size: 0.75rem; font-weight: 700; color: {p_color}; text-transform: uppercase;">{step.get('week_range', f'Phase {idx+1}')} — {step.get('phase_title', '')}</div>
                        <p style="font-size: 0.925rem; color: #CBD5E1; margin: 4px 0;"><b>Focus Area:</b> {step.get('focus', '')}</p>
                        <p style="font-size: 0.85rem; color: #94A3B8; margin: 0;"><b>Target Standard:</b> <span style="color: #38BDF8;">{step.get('target_standard', '')}</span></p>
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
