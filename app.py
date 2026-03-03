import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
import os

st.set_page_config(
    page_title="NexGen CV Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🌌"
)

# --- CLEAN MODERN CSS ---
st.markdown("""
<style>
    /* Clean Typography and minimalist style */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0B0E14 !important;
        color: #E2E8F0;
    }

    /* Ambient Background Glow */
    .stApp {
        background: radial-gradient(circle at 15% 50%, rgba(59, 130, 246, 0.08), transparent 50%),
                    radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.08), transparent 50%);
        background-color: #0B0E14;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        color: #F8FAFC !important;
    }

    h1 {
        text-align: center;
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
        font-size: 3.8rem !important;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #FFFFFF 0%, #A5B4FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #94A3B8;
        font-size: 1.25rem;
        margin-top: 5px;
        margin-bottom: 50px;
        font-weight: 400;
        font-family: 'Outfit', sans-serif;
        letter-spacing: 0.05em;
    }

    /* Streamlit Button Overrides */
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: 0.02em !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
    }

    /* File Uploader Container Box Styling Glassmorphism */
    div[data-testid="stFileUploader"] {
        background: rgba(30, 41, 59, 0.4);
        border: 1px dashed rgba(148, 163, 184, 0.3);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        transition: all 0.3s ease;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: rgba(99, 102, 241, 0.6);
        background: rgba(30, 41, 59, 0.6);
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.1);
    }
    
    /* Upload Text */
    div[data-testid="stFileUploader"] small {
        color: #94A3B8 !important;
    }

    /* Expanders styling */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.4) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
        color: #E2E8F0 !important;
    }

    div[data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }

    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif !important;
        color: #A5B4FC !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif !important;
        color: #94A3B8 !important;
    }

    /* Clean up default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    hr { 
        border: 0;
        height: 1px;
        background: linear-gradient(to right, rgba(0,0,0,0), rgba(255,255,255,0.1), rgba(0,0,0,0)); 
        margin: 3rem 0;
    }

    /* Custom Glass Panel Class for Layout */
    .glass-panel {
        background: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
        transition: transform 0.3s ease !important;
    }
    
    .glass-panel:hover {
        transform: translateY(-2px) !important;
    }
    
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("<h1>Pathfinder Global Intelligence</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Multilingual AI CV Parsing & Predictive Career Benchmarking</div>", unsafe_allow_html=True)

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
    c1, c2, c3 = st.columns([1,3,1])
    with c2:
        st.markdown("<h3 style='text-align:center; font-weight: 400; margin-bottom:15px; font-size: 1.4rem; color: #CBD5E1;'>Drop any CV • PDF or Image • Any Language</h3>", unsafe_allow_html=True)
        target_role = st.text_input("", placeholder="Target Role e.g., Senior AI Engineer (Optional)", label_visibility="collapsed")
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")
        
        if uploaded_file:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Generate Diagnostic Report ✨", use_container_width=True):
                contents = []
                
                with st.status("Initializing Quantum Analysis...", expanded=True) as status:
                    st.write("Extracting deep document features...")
                    try:
                        if uploaded_file.name.lower().endswith('.pdf'):
                            # Use native Gemini PDF parsing feature for flawless multilingual text extraction
                            pdf_data = uploaded_file.getvalue()
                            contents.append({
                                "mime_type": "application/pdf",
                                "data": pdf_data
                            })
                        else:
                            contents.append(Image.open(uploaded_file))
                    except Exception as e:
                        status.update(label=f"Document parsing failed: {e}", state="error")
                        st.stop()

                    st.write("Engaging multilingual predictive engine (Gemini 2.5 Flash)...")
                    
                    target_role_context = f"The user is specifically targeting the role of: '{target_role}'. Please include a prioritized skill gap analysis for this specific role." if target_role else "No specific target role provided. Provide a general career analysis without specific skill gaps."

                    prompt = f"""
                    You are an elite, world-class AI Career Strategist and Tech Analyst for a premium firm.
                    Analyze the attached candidate document. The document may be in ANY language (e.g., English, Spanish, German, French, Hindi, Japanese, etc.).
                    You must perfectly understand the candidate's profile, translate contexts internally, and output your comprehensive analysis STRICTLY in English.

                    {target_role_context}

                    Return ONLY valid JSON matching this exact structure:
                    {{
                        "executive_summary": "Professional, highly analytical 2-sentence breakdown of the candidate's core value. Use engaging, premium business language.",
                        "global_confidence_score": 88,
                        "primary_language_detected": "English",
                        "core_skills": [
                            {{"name": "Python", "score": 95}}, {{"name": "Architecture", "score": 85}}, {{"name": "Agile", "score": 70}}
                        ],
                        "career_trajectories": [
                            {{"role": "Primary Vector", "match_probability": 94, "rationale": "High transferability due to..."}}
                        ],
                        "competency_radar": [
                            {{"axis": "Technical Expertise", "value": 85}}, {{"axis": "Leadership", "value": 60}}, 
                            {{"axis": "Communication", "value": 75}}, {{"axis": "System Design", "value": 90}},
                            {{"axis": "Business Acumen", "value": 50}}
                        ],
                        "skill_gaps": [
                            {{"skill": "Missing Skill", "priority": "High", "rationale": "Crucial for target role."}}
                        ] // Leave empty ([]) if no target role is specified. Priority should be High, Medium, or Low.
                    }}
                    """
                    
                    contents.insert(0, prompt)

                    try:
                        genai.configure(api_key=API_KEY)
                        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
                        
                        response = model.generate_content(contents)
                            
                        st.write("Synthesizing neural matrix...")
                        time.sleep(0.5)
                        st.session_state.data = json.loads(response.text)
                        # Fallback for old schema
                        if "primary_language_detected" not in st.session_state.data:
                             st.session_state.data["primary_language_detected"] = "Unknown"
                        st.session_state.analysis_complete = True
                        status.update(label="Evaluation Complete", state="complete", expanded=False)
                        st.rerun()
                    except Exception as e:
                        status.update(label=f"Analysis Engine Failed: {e}", state="error")
                        st.stop()


# --- INTERACTIVE DASHBOARD VIEW ---
if st.session_state.analysis_complete:
    data = st.session_state.data
    
    col_exec, col_gauge = st.columns([2.2, 1])
    
    with col_exec:
        # Generate skill gap html if any
        skill_gap_html = ""
        if data.get("skill_gaps") and len(data["skill_gaps"]) > 0:
            skill_gap_html += "<br><br><h3 style='margin-bottom: 15px;'>🎯 Target Skill Gaps</h3>"
            for gap in data["skill_gaps"]:
                color = "#EF4444" if gap.get("priority") == "High" else ("#F59E0B" if gap.get("priority") == "Medium" else "#10B981")
                rgba_color = "rgba(239, 68, 68, 0.15)" if gap.get("priority") == "High" else ("rgba(245, 158, 11, 0.15)" if gap.get("priority") == "Medium" else "rgba(16, 185, 129, 0.15)")
                skill_gap_html += f"""
                <div style="background: {rgba_color}; border-left: 3px solid {color}; padding: 12px 16px; margin-bottom: 10px; border-radius: 0 8px 8px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-weight: 600; font-family: 'Outfit'; color: #F8FAFC; font-size: 1.05rem;">{gap.get('skill', '')}</span>
                        <span style="font-size: 0.75rem; font-weight: 700; background: {color}; color: white; padding: 2px 8px; border-radius: 12px; font-family: 'Inter';">{gap.get('priority', '')}</span>
                    </div>
                    <p style="margin: 0; font-size: 0.9rem; color: #CBD5E1; line-height: 1.4;">{gap.get('rationale', '')}</p>
                </div>
                """
        
        st.markdown(f"""
        <div class="glass-panel" style="height: 100%;">
            <h3 style='margin-top:0;'>Executive Profile</h3>
            <p style='font-size: 1.1rem; line-height: 1.6; color: #E2E8F0;'>{data['executive_summary']}</p>
            <div style='margin-top: 15px; display: inline-block; background: rgba(139, 92, 246, 0.2); border: 1px solid rgba(139, 92, 246, 0.5); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; color: #C4B5FD;'>
                🌐 Source Language Detected: {data.get('primary_language_detected', 'Unknown')}
            </div>
            {skill_gap_html}
            <br><br>
            <h3 style='margin-bottom: 20px;'>Evaluated Competencies</h3>
            {" ".join([f"<span style='background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%); border: 1px solid rgba(148, 163, 184, 0.2); padding: 6px 16px; border-radius: 20px; color: #E2E8F0; display: inline-block; margin-bottom: 12px; margin-right: 8px; font-size: 0.95rem; font-family: Outfit; font-weight: 500; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>{skill['name']} <span style='color: #60A5FA; font-weight: 700;'>{skill['score']}%</span></span>" for skill in data['core_skills'] if skill['score'] > 40])}
        </div>
        """, unsafe_allow_html=True)

    with col_gauge:
        st.markdown("<div class='glass-panel' style='height: 100%; display: flex; flex-direction: column; justify-content: center;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-top:0;'>Global Fit Score</h3>", unsafe_allow_html=True)
        # Infographic 1: Gauge Chart for Overall Fit
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = data.get("global_confidence_score", 85),
            domain = {'x': [0, 1], 'y': [0, 1]},
            number = {'font': {'color': '#F8FAFC', 'family': 'Outfit', 'size': 48}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
                'bar': {'color': "#60A5FA"},
                'bgcolor': "rgba(30, 41, 59, 0.5)",
                'borderwidth': 0,
                'bordercolor': "transparent",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.2)'},
                    {'range': [50, 80], 'color': 'rgba(245, 158, 11, 0.2)'},
                    {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.2)'}],
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            font={'color': "#F8FAFC", 'family': "Outfit"},
            height=250,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align: center; margin-bottom: 30px;'>Target Career Trajectories</h2>", unsafe_allow_html=True)
    
    # Interactive Element: Expanders
    # We will use Streamlit expanders wrapped in our CSS for a glassy look
    for i, row in enumerate(data["career_trajectories"]):
        with st.expander(f"🚀 {row['role']}   —   {row['match_probability']}% Compatibility", expanded=(i==0)):
            m_col1, m_col2 = st.columns([1, 4])
            with m_col1:
                st.metric(label="Match Probability", value=f"{row['match_probability']}%")
            with m_col2:
                st.write("**Alignment Strategy:**")
                st.write(row['rationale'])
            st.progress(row['match_probability'] / 100.0)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_radar, col_bar = st.columns(2)
    
    with col_radar:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-top:0;'>Competency Matrix</h3>", unsafe_allow_html=True)
        # Infographic 2: Radar Chart
        df_radar = pd.DataFrame(data["competency_radar"])
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=df_radar['value'],
            theta=df_radar['axis'],
            fill='toself',
            fillcolor='rgba(99, 102, 241, 0.25)',
            line=dict(color='#818CF8', width=3),
            marker=dict(color='#E0E7FF', size=8)
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color="#475569", gridcolor="rgba(148, 163, 184, 0.2)", showticklabels=False),
                angularaxis=dict(color="#CBD5E1", gridcolor="rgba(148, 163, 184, 0.2)", tickfont=dict(size=14, family='Outfit'))
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=30, b=30),
            height=380
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_bar:
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-top:0;'>Skill Proficiency Index</h3>", unsafe_allow_html=True)
        # Infographic 3: Bar Chart
        df_skills = pd.DataFrame(data["core_skills"]).sort_values(by='score', ascending=True)
        
        # Neon bar chart
        fig_bar = px.bar(
            df_skills, 
            x='score', 
            y='name', 
            orientation='h',
            color='score',
            color_continuous_scale=[[0, 'rgba(59, 130, 246, 0.3)'], [1, 'rgba(139, 92, 246, 0.9)']]
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(range=[0,100], showline=False, showgrid=True, gridcolor='rgba(148, 163, 184, 0.1)', title='Proficiency %', tickfont=dict(color='#64748B')),
            yaxis=dict(title='', tickfont=dict(color='#E2E8F0', size=14, family='Outfit')),
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=20, t=30, b=30),
            height=380
        )
        fig_bar.update_traces(marker_line_width=0, opacity=0.9)
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    c_btn1, c_btn2, c_btn3 = st.columns([1,2,1])
    if c_btn2.button("✧ Process Another Candidate ✧", use_container_width=True):
        st.session_state.analysis_complete = False
        st.rerun()
