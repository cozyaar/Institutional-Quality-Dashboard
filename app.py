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
import textwrap

st.set_page_config(
    page_title="Pathfinder Intelligence",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ADVANCED CYBER/GLASS ANIMATED CSS ---
st.markdown("""
<style>
    /* Global Animations & Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Ambient Shifting Background */
    .stApp {
        background: radial-gradient(circle at 15% 50%, rgba(139, 92, 246, 0.15), transparent 25%),
                    radial-gradient(circle at 85% 30%, rgba(56, 189, 248, 0.15), transparent 25%);
        background-color: #09090B;
        background-size: 200% 200%;
        animation: floatBg 15s ease infinite alternate;
        color: #FAFAFA;
    }
    
    @keyframes floatBg {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Glowing Text FX */
    h1 {
        font-weight: 800 !important;
        background: linear-gradient(to right, #A78BFA, #38BDF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 4rem !important;
        line-height: 1.1;
        animation: glowText 3s ease-in-out infinite alternate;
    }
    
    @keyframes glowText {
        from { text-shadow: 0 0 10px rgba(167, 139, 250, 0.1), 0 0 20px rgba(56, 189, 248, 0.1); }
        to { text-shadow: 0 0 20px rgba(167, 139, 250, 0.3), 0 0 30px rgba(56, 189, 248, 0.2); }
    }
    
    .subtitle {
        text-align: center;
        color: #A1A1AA;
        font-size: 1.25rem;
        margin-bottom: 3rem;
        letter-spacing: 0.05em;
    }

    /* Native Interactive Button overriding */
    .stButton > button {
        background: linear-gradient(135deg, #7C3AED 0%, #0284C7 100%) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        letter-spacing: 1px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 0 20px rgba(124, 58, 237, 0.4) !important;
        text-transform: uppercase;
    }
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 10px 30px rgba(56, 189, 248, 0.6) !important;
        border-color: rgba(255,255,255,0.3) !important;
    }

    /* Streamlit Tabs Customization - Cyber Style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding: 10px 0;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #A1A1AA;
        transition: all 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(124, 58, 237, 0.1) !important;
        color: #A78BFA !important;
        border-bottom: 2px solid #A78BFA !important;
    }

    /* Fix Uploader Box */
    div[data-testid="stFileUploader"] {
        background: rgba(24, 24, 27, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 30px;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
    }
    
    /* Plotly Chart fixes */
    .js-plotly-plot .plotly .modebar {
        display: none !important;
    }
    
    /* Clean up default hr */
    hr { display: none !important; }

</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("<h1>QUANTUM PATHFINDER</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>PREDICTIVE NEURAL CAREER DIAGNOSTICS</div>", unsafe_allow_html=True)

# --- SECURE AUTHENTICATION CHECK ---
try:
    API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not API_KEY:
        st.error("### 🛑 SYSTEM OFFLINE: MISSING AUTHENTICATION KEY")
        st.stop()
except Exception as e:
     st.error(f"Configuration Error: {e}")
     st.stop()

# --- STATE INIT ---
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

# --- INPUT VIEW ---
if not st.session_state.analysis_complete:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<h3 style='text-align:center; color:#E4E4E7; font-weight: 300; margin-bottom:15px;'>UPLOAD SUBJECT DATA MATRIX</h3>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Drop PDF or Image", type=["pdf", "png", "jpg", "jpeg"], label_visibility="collapsed")
        
        if uploaded_file:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("INITIALIZE NEURAL ANALYSIS", use_container_width=True):
                resume_text = ""
                image_parts = []
                
                with st.status("Establishing AI uplink...", expanded=True) as status:
                    st.write("Extracting binary data...")
                    try:
                        if uploaded_file.name.lower().endswith('.pdf'):
                            for page in PyPDF2.PdfReader(uploaded_file).pages:
                                t = page.extract_text()
                                if t: resume_text += t + "\n"
                        else:
                            image_parts.append(Image.open(uploaded_file))
                    except Exception as e:
                        status.update(label="Extraction Failed", state="error")
                        st.stop()

                    st.write("Synthesizing vectors with Gemini 2.5 Flash Engine...")
                    
                    prompt = """
                    You are a hyper-intelligent AI career analyst. Return ONLY valid JSON:
                    {
                        "executive_summary": "Intense, professional 2-sentence breakdown of the candidate's core value.",
                        "core_skills": [
                            {"name": "Python", "score": 95}, {"name": "Architecture", "score": 85}, {"name": "Agile", "score": 70}
                        ],
                        "career_trajectories": [
                            {"role": "Primary Vector", "match_probability": 94, "rationale": "Perfect synergy..."},
                            {"role": "Secondary Vector", "match_probability": 82, "rationale": "High transferability..."}
                        ],
                        "competency_radar": [
                            {"axis": "Technical", "value": 85}, {"axis": "Leadership", "value": 60}, 
                            {"axis": "Communication", "value": 75}, {"axis": "System Design", "value": 90},
                            {"axis": "Business Strategy", "value": 50}
                        ]
                    }
                    """

                    try:
                        genai.configure(api_key=API_KEY)
                        model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
                        
                        response = model.generate_content([prompt, image_parts[0]]) if image_parts else model.generate_content(prompt)
                            
                        st.write("Compiling visual representations...")
                        time.sleep(0.5)
                        st.session_state.data = json.loads(response.text)
                        st.session_state.analysis_complete = True
                        status.update(label="Analysis Complete", state="complete", expanded=False)
                        st.rerun()
                    except Exception as e:
                        status.update(label="Neural Link Failed", state="error")
                        st.stop()


# --- INTERACTIVE TABBED DASHBOARD VIEW ---
if st.session_state.analysis_complete:
    data = st.session_state.data
    
    # 1. INTERACTIVE TABS TO SOLVE SCROLLBAR/CLUTTER ISSUES!
    tab1, tab2, tab3 = st.tabs(["🚀 STRATEGIC OVERVIEW", "🎯 CAREER VECTORS", "🧬 SKILL MATRIX"])
    
    # TAB 1: OVERVIEW
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        colA, colB = st.columns([1.5, 1])
        with colA:
            # We use dedent technique by building string cleanly line by line, no spaces!
            html_chunk = []
            html_chunk.append("<div style='background:rgba(24,24,27,0.6); padding:30px; border-radius:16px; border:1px solid rgba(255,255,255,0.05); box-shadow:0 10px 30px rgba(0,0,0,0.5);'>")
            html_chunk.append("<h2 style='color:#FAFAFA; font-weight:800; margin-top:0;'>EXECUTIVE PROFILE</h2>")
            html_chunk.append(f"<p style='color:#A1A1AA; font-size:1.2rem; line-height:1.7;'>{data['executive_summary']}</p>")
            html_chunk.append("<br><h4 style='color:#A78BFA; letter-spacing:1px;'>VERIFIED COMPETENCIES</h4>")
            html_chunk.append("<div>")
            for skill in data['core_skills']:
                if skill['score'] > 60:
                    html_chunk.append(f"<span style='display:inline-block; background:rgba(124,58,237,0.15); color:#D8B4FE; border:1px solid rgba(124,58,237,0.4); padding:8px 16px; border-radius:20px; font-weight:600; margin:5px; box-shadow:0 0 10px rgba(124,58,237,0.2); transition:all 0.3s;'>{skill['name']}</span>")
            html_chunk.append("</div></div>")
            
            st.markdown("".join(html_chunk), unsafe_allow_html=True)
            
        with colB:
            # An animated call out box
            callout = []
            callout.append("<div style='background:linear-gradient(135deg, rgba(8,145,178,0.2), rgba(124,58,237,0.2)); padding:30px; border-radius:16px; border:1px solid rgba(167,139,250,0.3);text-align:center;'>")
            callout.append("<h1 style='font-size:4rem; margin:0; background:linear-gradient(to right, #38BDF8, #A78BFA); -webkit-background-clip:text; color:transparent; animation:none;'>")
            callout.append(f"{data['career_trajectories'][0]['match_probability']}%")
            callout.append("</h1>")
            callout.append("<h3 style='color:#E4E4E7; letter-spacing:2px; margin-top:0;'>PRIMARY ALIGNMENT</h3>")
            callout.append(f"<p style='color:#38BDF8; font-size:1.2rem; font-weight:600;'>{data['career_trajectories'][0]['role']}</p>")
            callout.append("</div>")
            st.markdown("".join(callout), unsafe_allow_html=True)

    # TAB 2: VECTORS
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        html_vectors = []
        html_vectors.append("<div style='display:grid; gap:20px;'>")
        for i, row in enumerate(data["career_trajectories"]):
            b_color = "#A78BFA" if i==0 else "#38BDF8"
            bg_color = "rgba(124,58,237,0.1)" if i==0 else "rgba(24,24,27,0.6)"
            border = f"1px solid rgba(167,139,250,0.4)" if i==0 else "1px solid rgba(255,255,255,0.05)"
            html_vectors.append(f"<div style='background:{bg_color}; border:{border}; border-left:4px solid {b_color}; padding:25px; border-radius:12px; transition:transform 0.2s;' onmouseover='this.style.transform=\"translateX(10px)\"' onmouseout='this.style.transform=\"none\"'>")
            html_vectors.append(f"<div style='display:flex; justify-content:space-between; align-items:center;'>")
            html_vectors.append(f"<h2 style='margin:0; color:#FAFAFA;'>{row['role']}</h2>")
            html_vectors.append(f"<h2 style='margin:0; color:{b_color}; text-shadow:0 0 10px {b_color};'>{row['match_probability']}% MATCH</h2>")
            html_vectors.append("</div>")
            html_vectors.append(f"<p style='color:#A1A1AA; font-size:1.1rem; line-height:1.6; margin-top:10px;'>{row['rationale']}</p>")
            html_vectors.append("</div>")
        html_vectors.append("</div>")
        st.markdown("".join(html_vectors), unsafe_allow_html=True)

    # TAB 3: MATRIX & RADAR - FITS PERFECTLY IN ITS OWN HUGE WINDOW
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        r_col, l_col = st.columns(2)
        
        with r_col:
            st.markdown("<h3 style='color:#FAFAFA; text-align:center;'>NEURAL COMPETENCY RADAR</h3>", unsafe_allow_html=True)
            df_radar = pd.DataFrame(data["competency_radar"])
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=df_radar['value'],
                theta=df_radar['axis'],
                fill='toself',
                fillcolor='rgba(167, 139, 250, 0.3)',
                line=dict(color='#A78BFA', width=3),
                marker=dict(color='#FAFAFA', size=8)
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], color="#52525B", gridcolor="rgba(255,255,255,0.05)", showticklabels=False),
                    angularaxis=dict(color="#E4E4E7", gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=14, family='Outfit'))
                ),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=50, r=50, t=30, b=30),
                height=450
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with l_col:
            st.markdown("<h3 style='color:#FAFAFA; text-align:center;'>INDEX METRICS</h3>", unsafe_allow_html=True)
            df_skills = pd.DataFrame(data["core_skills"]).sort_values(by='score', ascending=True)
            fig_bar = px.bar(
                df_skills, 
                x='score', 
                y='name', 
                orientation='h',
                color='score',
                color_continuous_scale=[[0, 'rgba(56, 189, 248, 0.2)'], [1, '#A78BFA']]
            )
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0,100], showline=False, showgrid=True, gridcolor='rgba(255,255,255,0.05)', title='PROFICIENCY %', tickfont=dict(color='#71717A')),
                yaxis=dict(title='', tickfont=dict(color='#E4E4E7', size=15, family='Outfit')),
                showlegend=False,
                coloraxis_showscale=False,
                margin=dict(l=0, r=20, t=30, b=30),
                height=450
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    c_btn1, c_btn2, c_btn3 = st.columns([1,2,1])
    if c_btn2.button("⟳ INITIATE NEW SCAN SEQUENCE", use_container_width=True):
        st.session_state.analysis_complete = False
        st.rerun()
