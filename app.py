import streamlit as st
import google.generativeai as genai
import PyPDF2
import json
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
import os

st.set_page_config(
    page_title="Pathfinder Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CLEAN MODERN CSS ---
st.markdown("""
<style>
    /* Clean Typography and minimalist style */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
    }

    h1 {
        text-align: center;
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
        font-size: 3rem !important;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        text-align: center;
        color: #94A3B8;
        font-size: 1.1rem;
        margin-top: 5px;
        margin-bottom: 40px;
        font-weight: 400;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    /* Streamlit Button Overrides */
    .stButton > button {
        background-color: #3B82F6 !important;
        color: white !important;
        border: 1px solid #2563EB !important;
        border-radius: 6px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #2563EB !important;
        border-color: #1D4ED8 !important;
        transform: translateY(-1px) !important;
    }

    /* Container Box Styling */
    div[data-testid="stFileUploader"] {
        background-color: #1E293B;
        border: 1px dashed #475569;
        border-radius: 8px;
        padding: 20px;
    }
    
    /* Clean up default Streamlit elements */
    .st-emotion-cache-1wivap2 {
        display: none !important;
    }
    
    hr { display: none !important; }
    
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("<h1>Pathfinder Diagnostic System</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Predictive Career Intelligence & Industry Benchmarking</div>", unsafe_allow_html=True)

# --- SECURE AUTHENTICATION CHECK ---
try:
    API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not API_KEY:
        st.error("System Error: Missing Authentication Key.")
        st.stop()
except Exception as e:
     st.error(f"Configuration Error: {e}")
     st.stop()

# --- STATE INIT ---
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

# --- INPUT VIEW ---
if not st.session_state.analysis_complete:
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<h3 style='text-align:center; font-weight: 500; margin-bottom:15px; font-size: 1.5rem;'>Upload Subject Profile</h3>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Drop PDF or Image Profile", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")
        
        if uploaded_file:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Generate Diagnostic Report", use_container_width=True):
                resume_text = ""
                image_parts = []
                
                with st.status("Initializing Analysis...", expanded=True) as status:
                    st.write("Extracting document features...")
                    try:
                        if uploaded_file.name.lower().endswith('.pdf'):
                            for page in PyPDF2.PdfReader(uploaded_file).pages:
                                t = page.extract_text()
                                if t: resume_text += t + "\n"
                        else:
                            image_parts.append(Image.open(uploaded_file))
                    except Exception as e:
                        status.update(label="Document parsing failed", state="error")
                        st.stop()

                    st.write("Executing predictive engine (Gemini 2.5)...")
                    
                    prompt = """
                    You are an expert AI Career Strategist and Tech Analyst for a premium firm.
                    Analyze the candidate document. Return ONLY valid JSON:
                    {
                        "executive_summary": "Professional, highly analytical 2-sentence breakdown of the candidate's core value.",
                        "global_confidence_score": 88,
                        "core_skills": [
                            {"name": "Python", "score": 95}, {"name": "Architecture", "score": 85}, {"name": "Agile", "score": 70}
                        ],
                        "career_trajectories": [
                            {"role": "Primary Vector", "match_probability": 94, "rationale": "High transferability due to..."}
                        ],
                        "competency_radar": [
                            {"axis": "Technical Expertise", "value": 85}, {"axis": "Leadership", "value": 60}, 
                            {"axis": "Communication", "value": 75}, {"axis": "System Design", "value": 90},
                            {"axis": "Business Acumen", "value": 50}
                        ]
                    }
                    """

                    try:
                        genai.configure(api_key=API_KEY)
                        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
                        
                        response = model.generate_content([prompt, image_parts[0]]) if image_parts else model.generate_content(prompt)
                            
                        st.write("Finalizing report structure...")
                        time.sleep(0.5)
                        st.session_state.data = json.loads(response.text)
                        st.session_state.analysis_complete = True
                        status.update(label="Evaluation Complete", state="complete", expanded=False)
                        st.rerun()
                    except Exception as e:
                        status.update(label="Analysis Engine Failed", state="error")
                        st.stop()


# --- INTERACTIVE DASHBOARD VIEW ---
if st.session_state.analysis_complete:
    data = st.session_state.data
    
    st.markdown("---")
    
    # Using strict Native Streamlit containers for bullet-proof layout
    col_exec, col_gauge = st.columns([2, 1])
    
    with col_exec:
        st.subheader("Executive Profile")
        st.write(data['executive_summary'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Evaluated Competencies")
        
        # Interactive pill mapping
        skills_tags = [f"{skill['name']} ({skill['score']}%)" for skill in data['core_skills'] if skill['score'] > 60]
        st.markdown(
            " &nbsp;&nbsp;".join([f"<span style='background:#3B82F6; padding: 4px 12px; border-radius: 4px; color: white; display: inline-block; margin-bottom: 8px; font-size: 0.9rem;'>{tag}</span>" for tag in skills_tags]),
            unsafe_allow_html=True
        )

    with col_gauge:
        # Infographic 1: Gauge Chart for Overall Fit
        st.subheader("Global Fit Score")
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = data.get("global_confidence_score", 85),
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#334155"},
                'bar': {'color': "#3B82F6"},
                'bgcolor': "#1E293B",
                'borderwidth': 2,
                'bordercolor': "#334155",
                'steps': [
                    {'range': [0, 50], 'color': '#0F172A'},
                    {'range': [50, 80], 'color': '#1E293B'}],
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor="#0F172A", 
            font={'color': "#F8FAFC", 'family': "Inter"},
            height=250,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})

    st.markdown("---")
    
    st.subheader("Target Career Trajectories")
    # Interactive Element: Expanders
    for i, row in enumerate(data["career_trajectories"]):
        with st.expander(f"{row['role']}   —   {row['match_probability']}% Compatibility", expanded=(i==0)):
            st.metric(label="Match Probability", value=f"{row['match_probability']}%")
            st.write("**Alignment Rationale:**")
            st.write(row['rationale'])
            st.progress(row['match_probability'] / 100.0)

    st.markdown("---")
    
    col_radar, col_bar = st.columns(2)
    
    with col_radar:
        # Infographic 2: Radar Chart
        st.subheader("Competency Matrix")
        df_radar = pd.DataFrame(data["competency_radar"])
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=df_radar['value'],
            theta=df_radar['axis'],
            fill='toself',
            fillcolor='rgba(59, 130, 246, 0.2)',
            line=dict(color='#3B82F6', width=2),
            marker=dict(color='#F8FAFC', size=6)
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color="#475569", gridcolor="#1E293B", showticklabels=False),
                angularaxis=dict(color="#94A3B8", gridcolor="#1E293B", tickfont=dict(size=12, family='Inter'))
            ),
            showlegend=False,
            paper_bgcolor='#0F172A',
            plot_bgcolor='#0F172A',
            margin=dict(l=40, r=40, t=30, b=30),
            height=350
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})

    with col_bar:
        # Infographic 3: Bar Chart
        st.subheader("Skill Proficiency Index")
        df_skills = pd.DataFrame(data["core_skills"]).sort_values(by='score', ascending=True)
        fig_bar = px.bar(
            df_skills, 
            x='score', 
            y='name', 
            orientation='h',
            color='score',
            color_continuous_scale=[[0, '#1E293B'], [1, '#3B82F6']]
        )
        fig_bar.update_layout(
            paper_bgcolor='#0F172A',
            plot_bgcolor='#0F172A',
            xaxis=dict(range=[0,100], showline=False, showgrid=True, gridcolor='#1E293B', title='Proficiency %', tickfont=dict(color='#64748B')),
            yaxis=dict(title='', tickfont=dict(color='#94A3B8', size=13, family='Inter')),
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=20, t=30, b=30),
            height=350
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<br>", unsafe_allow_html=True)
    c_btn1, c_btn2, c_btn3 = st.columns([1,2,1])
    if c_btn2.button("Process Alternative Candidate", use_container_width=True):
        st.session_state.analysis_complete = False
        st.rerun()
