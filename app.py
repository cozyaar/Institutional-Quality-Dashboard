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
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed" # Starts collapsed for dramatic effect
)

# --- ADVANCED CSS & ANIMATIONS ---
st.markdown("""
<style>
    :root {
        --bg-dark: #09090b;
        --bg-card: rgba(24, 24, 27, 0.6);
        --primary: #10b981;
        --secondary: #0ea5e9;
        --text: #f8fafc;
        --text-muted: #94a3b8;
    }
    
    /* Dark Theme Base */
    .stApp {
        background-color: var(--bg-dark);
        color: var(--text);
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(16, 185, 129, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(14, 165, 233, 0.05) 0%, transparent 40%);
        background-attachment: fixed;
    }

    /* Typography & Glow Effects */
    h1 {
        font-family: 'Inter', 'SF Pro Display', sans-serif;
        font-weight: 900 !important;
        background: linear-gradient(135deg, #34d399 0%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        letter-spacing: -0.05em;
        margin-bottom: 0 !important;
        animation: glow 4s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 10px rgba(52, 211, 153, 0.1), 0 0 20px rgba(52, 211, 153, 0.05); }
        to { text-shadow: 0 0 15px rgba(56, 189, 248, 0.2), 0 0 25px rgba(56, 189, 248, 0.1); }
    }

    .subtitle-text {
        text-align: center;
        color: var(--text-muted);
        font-size: 1.2rem;
        margin-bottom: 3rem;
        font-weight: 300;
        letter-spacing: 0.05em;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 24px -2px rgba(0, 0, 0, 0.5);
        transition: transform 0.3s ease, border-color 0.3s ease;
        animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        opacity: 0;
        transform: translateY(20px);
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(16, 185, 129, 0.3);
    }

    @keyframes slideUp {
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Reveal delays for staggered entrance */
    .delay-1 { animation-delay: 0.1s; }
    .delay-2 { animation-delay: 0.2s; }
    .delay-3 { animation-delay: 0.3s; }
    .delay-4 { animation-delay: 0.4s; }

    /* Custom Streamlit Elements Override */
    div[data-testid="metric-container"] {
        background: rgba(255,255,255,0.03);
        border-left: 4px solid var(--primary);
        padding: 15px;
        border-radius: 8px;
    }
    
    /* Neon Pills */
    .neon-pill {
        display: inline-block;
        padding: 6px 14px;
        margin: 4px;
        border-radius: 4px; /* Flatter, tech feel opposed to bubbly */
        background: rgba(16, 185, 129, 0.08);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.2);
        font-size: 0.85rem;
        font-family: monospace;
        transition: all 0.2s ease;
    }
    .neon-pill:hover {
        background: rgba(16, 185, 129, 0.15);
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.2);
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        border: none;
        border-radius: 6px; /* Boxier for that hacker aesthetic */
        padding: 0.75rem 2rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.3);
    }
    
    /* Hide Streamlit components */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown('<h1>PATH-FINDER AI</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Predictive Career Trajectories & Skill Gap Synthesis</div>', unsafe_allow_html=True)

# --- UPLOAD SECTION (Centered for impact) ---
upload_col1, upload_col2, upload_col3 = st.columns([1, 2, 1])

with upload_col2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:white; margin-bottom: 20px;'>Initialize Neural Scan</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Ingest Candidate Data (PDF, PNG, JPG)", 
        type=["pdf", "png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

if not uploaded_file:
    # Dramatic empty state
    st.markdown("""
        <div style='text-align:center; margin-top:50px; color:rgba(255,255,255,0.3);'>
            <i>SYSTEM STANDBY • AWAITING DATA INGESTION</i>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- BACKEND LOGIC & AI ---
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False

# We use a button to trigger, but center it.
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
analyze_clicked = col_btn2.button("EXECUTE ANALYSIS PROTOCOL", use_container_width=True)

if analyze_clicked or st.session_state.analysis_complete:
    if not st.session_state.analysis_complete:
        resume_text = ""
        image_parts = []
        
        # --- Dramatic Loading Sequence ---
        progress_bar = st.empty()
        status_text = st.empty()
        
        with progress_bar:
            st.progress(0)
        
        status_text.markdown("<p style='text-align:center; color:#60a5fa;'>Parsing binary formats...</p>", unsafe_allow_html=True)
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
            st.error(f"SYSTEM FAULT: {e}")
            st.stop()

        with progress_bar: st.progress(30)
        status_text.markdown("<p style='text-align:center; color:#10b981; font-family:monospace;'>[ > ] SYNTHESIZING NEURAL VECTORS...</p>", unsafe_allow_html=True)
        time.sleep(0.5)
        prompt = """
        You are a highly advanced predictive Career Intelligence Engine. 
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
                {"axis": "Technical", "value": 85},
                {"axis": "Leadership", "value": 60},
                {"axis": "Communication", "value": 75},
                {"axis": "Problem Solving", "value": 90},
                {"axis": "Industry Knowledge", "value": 50}
            ],
            "roadmap": [
                {"phase": "Phase 1: Immediate", "focus": "Critical Gap", "action": "Specific Action"}
            ]
        }
        """

        try:
            # First try Streamlit secrets
            api_key_to_use = None
            try:
                api_key_to_use = st.secrets.get("GEMINI_API_KEY", "")
            except Exception:
                pass
                
            # Fallback for local execution
            if not api_key_to_use:
                # Add default key safely
                api_key_to_use = "AIzaSyCLvNo6ebdPCb8hGOnQ-at4u4odJQB75kI"
                
            genai.configure(api_key=api_key_to_use)
            model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
            
            with progress_bar: st.progress(60)
            status_text.markdown("<p style='text-align:center; color:#0ea5e9; font-family:monospace;'>[ > ] GENERATING PREDICTIVE TRAJECTORIES...</p>", unsafe_allow_html=True)
            
            if image_parts:
                response = model.generate_content([prompt, image_parts[0]])
            else:
                response = model.generate_content(prompt)
                
            with progress_bar: st.progress(90)
            status_text.markdown("<p style='text-align:center; color:#6ee7b7; font-family:monospace;'>[ > ] RENDERING VISUALIZATION DASHBOARD...</p>", unsafe_allow_html=True)
            time.sleep(0.5)
            
            st.session_state.data = json.loads(response.text)
            st.session_state.analysis_complete = True
            
            progress_bar.empty()
            status_text.empty()
            st.rerun() # Refresh to show results cleanly
            
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"ANALYSIS FAILED: {str(e)}")
            st.stop()

    # --- RESULTS DASHBOARD ---
    if st.session_state.analysis_complete:
        data = st.session_state.data
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        
        # 1. TOP ROW: Summary & Radar Chart
        row1_col1, row1_col2 = st.columns([1, 1])
        
        with row1_col1:
            st.markdown('<div class="glass-card delay-1">', unsafe_allow_html=True)
            st.markdown("<h3 style='color:white; margin-bottom:15px;'>Executive Profile</h3>", unsafe_allow_html=True)
            st.write(data["executive_summary"])
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("<h4 style='color:#94a3b8; font-size:1rem;'>Verified Capabilities</h4>", unsafe_allow_html=True)
            badges_html = "".join([f'<span class="neon-pill">{skill["name"]}</span>' for skill in data["core_skills"]])
            st.markdown(badges_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with row1_col2:
            st.markdown('<div class="glass-card delay-2">', unsafe_allow_html=True)
            st.markdown("<h3 style='color:white; margin-bottom:0px; text-align:center;'>Competency Matrix</h3>", unsafe_allow_html=True)
            
            # --- PLOTLY RADAR CHART ---
            df_radar = pd.DataFrame(data["competency_radar"])
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=df_radar['value'],
                theta=df_radar['axis'],
                fill='toself',
                fillcolor='rgba(16, 185, 129, 0.2)',
                line=dict(color='#10b981', width=2),
                marker=dict(color='#34d399', size=6)
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], color="#64748b", gridcolor="rgba(255,255,255,0.05)"),
                    angularaxis=dict(color="#f8fafc", gridcolor="rgba(255,255,255,0.05)", tickfont=dict(size=12, family="monospace"))
                ),
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=40, t=20, b=20),
                height=300
            )
            st.plotly_chart(fig_radar, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

        # 2. MIDDLE ROW: Predictive Trajectories (Donut Chart & Metrics)
        st.markdown('<div class="glass-card delay-3">', unsafe_allow_html=True)
        st.markdown("<h3 style='color:white; margin-bottom:20px;'>Predictive Alignment Engine</h3>", unsafe_allow_html=True)
        
        traj_col1, traj_col2 = st.columns([1, 2])
        
        with traj_col1:
            # --- PLOTLY DONUT CHART ---
            df_traj = pd.DataFrame(data["career_trajectories"])
            # Create a "Remainding" value just to make the donut chart look cool for the top match
            top_match = df_traj.iloc[0]['match_probability']
            df_donut = pd.DataFrame({
                'Category': ['Match Score', 'Delta'],
                'Value': [top_match, 100 - top_match]
            })
            
            fig_donut = px.pie(
                df_donut, 
                values='Value', 
                names='Category', 
                hole=0.75,
                color_discrete_sequence=['#10b981', 'rgba(255,255,255,0.02)']
            )
            fig_donut.update_traces(textinfo='none', hoverinfo='none')
            fig_donut.update_layout(
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=0, b=0),
                height=250,
                annotations=[dict(text=f"{top_match}%", x=0.5, y=0.5, font_size=40, font_color="white", font_family="monospace", showarrow=False)]
            )
            st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})
            st.markdown(f"<p style='text-align:center; color:#94a3b8; font-family:monospace;'>OPTIMAL VECTOR: <br><b style='color:#34d399; font-size:1.1rem; font-family:sans-serif;'>{df_traj.iloc[0]['role']}</b></p>", unsafe_allow_html=True)

        with traj_col2:
            for i, row in df_traj.iterrows():
                # Streamlit metric UI trick
                st.markdown(f"""
                <div style='background:rgba(255,255,255,0.02); padding:15px; border-radius:6px; margin-bottom:10px; border-left:3px solid {"#10b981" if i==0 else "rgba(100,116,139,0.3)"};'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <h4 style='margin:0; color:white; font-weight:600;'>{row['role']}</h4>
                        <span style='color:{"#34d399" if i==0 else "#64748b"}; font-weight:bold; font-family:monospace;'>{row['match_probability']}%</span>
                    </div>
                    <p style='margin:5px 0 0 0; color:#94a3b8; font-size:0.9rem;'>{row['rationale']}</p>
                </div>
                """, unsafe_allow_html=True)
                
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 3. BOTTOM SECTION: Interactive Bar Chart for Specific Skills
        st.markdown('<div class="glass-card delay-4">', unsafe_allow_html=True)
        st.markdown("<h3 style='color:white; margin-bottom:20px;'>Skill Deep-Dive Metrics</h3>", unsafe_allow_html=True)
        
        df_skills = pd.DataFrame(data["core_skills"])
        fig_bar = px.bar(
            df_skills, 
            x='score', 
            y='name', 
            orientation='h',
            color='score',
            color_continuous_scale=[[0, 'rgba(14, 165, 233, 0.2)'], [1, '#10b981']]
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(range=[0,100], showline=False, showgrid=True, gridcolor='rgba(255,255,255,0.02)', title='Proficiency Index', tickfont=dict(color='#64748b', family="monospace")),
            yaxis=dict(title='', tickfont=dict(color='white', size=13)),
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=20, t=10, b=30),
            height=250
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Reset Button to do it again
        if st.button("↻ INTIALIZE NEW SCAN", use_container_width=True):
            st.session_state.analysis_complete = False
            st.rerun()
