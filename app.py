import streamlit as st
import google.generativeai as genai
import PyPDF2
import json
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time

st.set_page_config(
    page_title="Project Path-Finder | Career Intelligence",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MODERN LIGHT THEME CSS ---
st.markdown("""
<style>
    /* Typography & Core Styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    h1 {
        font-weight: 800 !important;
        color: #0F172A !important;
        letter-spacing: -0.02em;
        text-align: center;
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
    }
    
    .subtitle {
        text-align: center;
        color: #64748B;
        font-size: 1.25rem;
        font-weight: 400;
        margin-top: -10px;
        margin-bottom: 40px;
    }

    /* Primary Container / Cards */
    .premium-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        border: 1px solid #F1F5F9;
        margin-bottom: 24px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: fadeIn 0.5s ease-out forwards;
        opacity: 0;
        transform: translateY(10px);
    }
    
    .premium-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
        transform: translateY(-2px);
    }

    /* Staggered Animations */
    @keyframes fadeIn {
        to { opacity: 1; transform: translateY(0); }
    }
    .delay-1 { animation-delay: 0.1s; }
    .delay-2 { animation-delay: 0.2s; }
    .delay-3 { animation-delay: 0.3s; }
    .delay-4 { animation-delay: 0.4s; }

    /* Fancy Pills */
    .skill-pill {
        display: inline-block;
        padding: 6px 16px;
        margin: 4px;
        border-radius: 9999px;
        background: #EFF6FF;
        color: #1D4ED8;
        font-size: 0.875rem;
        font-weight: 600;
        border: 1px solid #DBEAFE;
    }

    /* Button Styling */
    .stButton > button {
        background-color: #2563EB !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #1D4ED8 !important;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3) !important;
        transform: translateY(-1px) !important;
    }

    /* Custom metrics */
    div[data-testid="metric-container"] {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .role-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }
    
    .role-match {
        color: #2563EB;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    .role-desc {
        color: #64748B;
        font-size: 0.9rem;
        margin-top: 8px;
    }
    
    hr {
        border-color: #E2E8F0;
    }

</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("<h1>Pathfinder<span style='color: #2563EB;'>AI</span> ✨</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Predictive Career Intelligence & Industry Benchmarking</div>", unsafe_allow_html=True)

# --- SECURE AUTHENTICATION CHECK ---
import os

try:
    # 1. Try Streamlit Secrets First (Local config OR Cloud Config)
    API_KEY = st.secrets.get("GEMINI_API_KEY")

    if not API_KEY:
        # 2. Try System Environment Variables (Sometimes needed on certain deployment configs)
        API_KEY = os.environ.get("GEMINI_API_KEY")

    if not API_KEY:
        # 3. Halt if nothing exists
        st.error("""
        ### 🛑 AUTHENTICATION REQUIRED
        You must provide a Google Gemini API Key to use this application. The previous key was disabled for security reasons.
        
        **How to fix:**
        1. Open the `.streamlit/secrets.toml` file in this directory.
        2. Set the key like this:
        `GEMINI_API_KEY = "your-new-google-gemini-key"`
        
        *If deployed to Streamlit Cloud, go to **App Settings > Secrets** and paste the same variable.*
        """)
        st.stop()
except Exception as e:
     st.error(f"Configuration Error: {e}")
     st.stop()

# --- UPLOAD SECTION ---
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

if not st.session_state.analysis_complete:
    st.markdown("<div style='max-width: 600px; margin: 0 auto;'>", unsafe_allow_html=True)
    st.markdown("<div class='premium-card' style='text-align: center;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin-bottom:20px; color:#0F172A;'>Upload Profile</h3>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Candidate Data (PDF, PNG, JPG)", 
        type=["pdf", "png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        if st.button("RUN INTELLIGENCE PROTOCOL", use_container_width=True):
            resume_text = ""
            image_parts = []
            
            with st.status("Analyzing Candidate Profile...", expanded=True) as status:
                st.write("Extracting data from file...")
                time.sleep(0.5)
                try:
                    if uploaded_file.name.lower().endswith('.pdf'):
                        pdf_reader = PyPDF2.PdfReader(uploaded_file)
                        for page in pdf_reader.pages:
                            t = page.extract_text()
                            if t: resume_text += t + "\n"
                    else:
                        img = Image.open(uploaded_file)
                        image_parts.append(img)
                except Exception as e:
                    status.update(label="File Extraction Failed", state="error")
                    st.error(str(e))
                    st.stop()

                st.write("Generating predictive trajectories via Gemini 2.5 Flash...")
                
                prompt = """
                You are a highly advanced predictive Career Intelligence Engine designed for a premium SaaS application. 
                Analyze the candidate document. Return ONLY valid JSON matching this exact structure:
                {
                    "executive_summary": "Intelligent, impactful 2-sentence summary of the candidate's potential.",
                    "core_skills": [
                        {"name": "Skill 1", "score": 95},
                        {"name": "Skill 2", "score": 80},
                        {"name": "Skill 3", "score": 60},
                        {"name": "Skill 4", "score": 45}
                    ],
                    "career_trajectories": [
                        {
                            "role": "Top Target Role Name",
                            "match_probability": 92,
                            "rationale": "Why this fits their profile."
                        },
                        {
                            "role": "Alternative Role 1",
                            "match_probability": 78,
                            "rationale": "Secondary fit rationale."
                        },
                        {
                            "role": "Alternative Role 2",
                            "match_probability": 65,
                            "rationale": "Tertiary fit rationale."
                        }
                    ],
                    "competency_radar": [
                        {"axis": "Technical Expertise", "value": 85},
                        {"axis": "Leadership", "value": 60},
                        {"axis": "Communication", "value": 75},
                        {"axis": "Architecture & Design", "value": 70},
                        {"axis": "Business Acumen", "value": 50}
                    ]
                }
                """

                try:
                    genai.configure(api_key=API_KEY)
                    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
                    
                    if image_parts:
                        response = model.generate_content([prompt, image_parts[0]])
                    else:
                        response = model.generate_content(prompt)
                        
                    st.write("Rendering intelligence dashboard...")
                    time.sleep(0.5)
                    st.session_state.data = json.loads(response.text)
                    st.session_state.analysis_complete = True
                    status.update(label="Analysis Complete", state="complete", expanded=False)
                    st.rerun()
                    
                except Exception as e:
                    status.update(label="AI Engine Error", state="error")
                    st.error(f"Failed to generate intelligence: {str(e)}")
                    st.stop()
                    
    st.markdown("</div></div>", unsafe_allow_html=True)


# --- DASHBOARD RESULTS ---
if st.session_state.analysis_complete:
    data = st.session_state.data
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='premium-card delay-1'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#0F172A; margin-top:0;'>Executive Profile</h3>", unsafe_allow_html=True)
        st.write(data["executive_summary"])
        
        st.markdown("<h4 style='color:#64748B; font-size:1rem; margin-top:20px;'>Core Competencies</h4>", unsafe_allow_html=True)
        badges_html = "".join([f"<span class='skill-pill'>{skill['name']}</span>" for skill in data["core_skills"] if skill['score'] > 60])
        st.markdown(badges_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='premium-card delay-3'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#0F172A; margin-top:0; margin-bottom: 20px;'>Predictive Outcomes</h3>", unsafe_allow_html=True)
        for i, row in enumerate(data["career_trajectories"]):
            st.markdown(f"""
            <div style='background:#F8FAFC; border:1px solid #E2E8F0; padding:16px; border-radius:12px; margin-bottom:12px; border-left:4px solid {"#2563EB" if i==0 else "#CBD5E1"};'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <p class='role-title'>{row['role']}</p>
                    <p class='role-match'>{row['match_probability']}%</p>
                </div>
                <p class='role-desc'>{row['rationale']}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='premium-card delay-2'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#0F172A; margin-top:0; text-align:center;'>Competency Matrix</h3>", unsafe_allow_html=True)
        
        # --- PLOTLY RADAR CHART: LIGHT MODE ---
        df_radar = pd.DataFrame(data["competency_radar"])
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=df_radar['value'],
            theta=df_radar['axis'],
            fill='toself',
            fillcolor='rgba(37, 99, 235, 0.15)',
            line=dict(color='#2563EB', width=2),
            marker=dict(color='#1E40AF', size=6)
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color="#94A3B8", gridcolor="#F1F5F9"),
                angularaxis=dict(color="#475569", gridcolor="#F1F5F9", tickfont=dict(size=12))
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=20, b=20),
            height=300
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='premium-card delay-4'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#0F172A; margin-top:0;'>Skill Index Assessment</h3>", unsafe_allow_html=True)
        
        df_skills = pd.DataFrame(data["core_skills"])
        fig_bar = px.bar(
            df_skills, 
            x='score', 
            y='name', 
            orientation='h',
            color='score',
            color_continuous_scale=[[0, '#DBEAFE'], [1, '#2563EB']]
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(range=[0,100], showline=False, showgrid=True, gridcolor='#F1F5F9', title='Proficiency Level', tickfont=dict(color='#64748B')),
            yaxis=dict(title='', tickfont=dict(color='#0F172A', size=13)),
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=20, t=10, b=30),
            height=250
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("<hr>", unsafe_allow_html=True)
    col_reset1, col_reset2, col_reset3 = st.columns([1, 1, 1])
    if col_reset2.button("← INGEST NEW CANDIDATE PROFILE", use_container_width=True):
        st.session_state.analysis_complete = False
        st.rerun()
