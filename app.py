import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

from ml_model import load_data, get_models, predict_student_readiness, calculate_pillar_scores, FEATURE_COLS
from utils import ROLE_TAXONOMY, analyze_resume_text, generate_custom_roadmap, DIAGNOSTIC_QUIZ

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Placement Readiness Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom CSS for Modern, Sleek UI
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 20px;
        color: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-bottom: 12px;
    }
    .metric-card-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .metric-card-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-card-subtitle {
        font-size: 0.82rem;
        color: #cbd5e1;
        margin-top: 4px;
    }
    
    /* Badges */
    .badge-tier1 {
        background-color: #10b981;
        color: white;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-tier2 {
        background-color: #3b82f6;
        color: white;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-tier3 {
        background-color: #f59e0b;
        color: white;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    /* Skill chips */
    .skill-chip {
        display: inline-block;
        padding: 4px 10px;
        margin: 3px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 500;
    }
    .chip-matched {
        background-color: #064e3b;
        color: #6ee7b7;
        border: 1px solid #059669;
    }
    .chip-missing {
        background-color: #450a0a;
        color: #fca5a5;
        border: 1px solid #dc2626;
    }
    .chip-opt-matched {
        background-color: #1e3a5f;
        color: #93c5fd;
        border: 1px solid #2563eb;
    }
    .chip-opt-missing {
        background-color: #1f2937;
        color: #9ca3af;
        border: 1px solid #4b5563;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Load Dataset & Models with Caching
# ---------------------------------------------------------
@st.cache_data
def get_cached_dataset():
    return load_data()

@st.cache_resource
def get_cached_models():
    return get_models()

df_cohort = get_cached_dataset()
_ = get_cached_models()

# ---------------------------------------------------------
# ---------------------------------------------------------
# Sidebar: Profile & Controls
# ---------------------------------------------------------
st.sidebar.image("https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3", use_container_width=True)
banner_img = os.path.join(os.path.dirname(os.path.abspath(__file__)), "placement_banner.jpg")
if os.path.exists(banner_img):
    st.sidebar.image(banner_img, use_container_width=True)
else:
    st.sidebar.image("https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3", use_container_width=True)
st.sidebar.title("👨‍🎓 Candidate Profile")
st.sidebar.caption("👉 You can enter custom values here or use the on-page form on the dashboard.")

preset = st.sidebar.selectbox(
    "⚡ Quick Load Profile Template",
    ["Custom Input", "High Achiever (Tier 1 Aim)", "Average Student (Needs Boost)", "Critical Attention Needed"]
)

if preset == "High Achiever (Tier 1 Aim)":
    init_branch = "Computer Science"
    init_cgpa = 8.90
    init_tenth = 92.0
    init_twelfth = 90.0
    init_dsa = 340
    init_projects = 4
    init_internships = 2
    init_hackathons = 3
    init_certs = 3
    init_aptitude = 88.0
    init_soft = 4.5
    init_backlogs = 0
elif preset == "Average Student (Needs Boost)":
    init_branch = "Information Technology"
    init_cgpa = 7.30
    init_tenth = 80.0
    init_twelfth = 76.0
    init_dsa = 110
    init_projects = 2
    init_internships = 0
    init_hackathons = 1
    init_certs = 1
    init_aptitude = 66.0
    init_soft = 3.4
    init_backlogs = 0
elif preset == "Critical Attention Needed":
    init_branch = "Electronics & Comm"
    init_cgpa = 6.10
    init_tenth = 68.0
    init_twelfth = 65.0
    init_dsa = 30
    init_projects = 1
    init_internships = 0
    init_hackathons = 0
    init_certs = 0
    init_aptitude = 48.0
    init_soft = 2.8
    init_backlogs = 2
else:
    init_branch = "Computer Science"
    init_cgpa = 8.10
    init_tenth = 85.0
    init_twelfth = 82.0
    init_dsa = 210
    init_projects = 3
    init_internships = 1
    init_hackathons = 2
    init_certs = 2
    init_aptitude = 75.0
    init_soft = 4.0
    init_backlogs = 0

# Sidebar Input Widgets
with st.sidebar.expander("📚 Academic Credentials", expanded=True):
    sb_branch = st.selectbox(
        "Engineering Branch",
        ["Computer Science", "Information Technology", "Electronics & Comm", "Electrical & Electronics", "Mechanical", "Civil"],
        index=["Computer Science", "Information Technology", "Electronics & Comm", "Electrical & Electronics", "Mechanical", "Civil"].index(init_branch),
        key="sb_branch"
    )
    sb_cgpa = st.number_input(
        "Undergrad CGPA (0.00 to 10.00)",
        min_value=0.0,
        max_value=10.0,
        value=float(init_cgpa),
        step=0.05,
        format="%.2f",
        help="Type your exact CGPA here",
        key="sb_cgpa"
    )
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sb_tenth = st.number_input("10th %", 0.0, 100.0, float(init_tenth), 0.5, format="%.1f", key="sb_tenth")
    with col_s2:
        sb_twelfth = st.number_input("12th %", 0.0, 100.0, float(init_twelfth), 0.5, format="%.1f", key="sb_twelfth")
    sb_backlogs = st.number_input("Active Backlogs", min_value=0, max_value=6, value=int(init_backlogs), step=1, key="sb_backlogs")

with st.sidebar.expander("💻 Coding & Technical Prowess", expanded=True):
    sb_dsa = st.number_input("DSA Problems Solved", min_value=0, max_value=1000, value=int(init_dsa), step=10, key="sb_dsa")
    sb_projects = st.number_input("Technical Capstone Projects", min_value=0, max_value=10, value=int(init_projects), step=1, key="sb_projects")
    sb_hackathons = st.number_input("Hackathons & Contests", min_value=0, max_value=10, value=int(init_hackathons), step=1, key="sb_hackathons")

with st.sidebar.expander("💼 Experience & Behavioral", expanded=False):
    sb_internships = st.number_input("Completed Internships", min_value=0, max_value=5, value=int(init_internships), step=1, key="sb_internships")
    sb_certs = st.number_input("Professional Certifications", min_value=0, max_value=10, value=int(init_certs), step=1, key="sb_certs")
    sb_aptitude = st.number_input("Aptitude Score (%)", 0.0, 100.0, float(init_aptitude), 1.0, format="%.1f", key="sb_aptitude")
    sb_soft_skills = st.number_input("Soft Skills Rating (1.0 - 5.0)", 1.0, 5.0, float(init_soft), 0.1, format="%.1f", key="sb_soft")

sb_target_role = st.sidebar.selectbox(
    "🎯 Target Dream Role",
    list(ROLE_TAXONOMY.keys()),
    index=0,
    key="sb_target_role"
)

# ---------------------------------------------------------
# Main Page Header & Dual Input Mode
# ---------------------------------------------------------
st.title("🎓 Campus Placement Readiness & Intelligence Dashboard")
st.markdown("An AI-powered diagnostic and decision platform for engineering graduates to evaluate placement eligibility, benchmark competencies, and unlock high-tier recruitment opportunities.")

# Direct Custom Profile Input Panel on Main Page
with st.expander("✏️ **CLICK HERE TO ENTER / EDIT CUSTOM PROFILE INPUTS (CGPA, BRANCH, DSA, BACKLOGS...)**", expanded=False):
    st.info("💡 **Custom Input**: You can type your exact CGPA, Branch, DSA problems, and other details right here below or in the **Left Sidebar** (click `>` at top-left if the sidebar is closed).")
    
    with st.form("main_profile_form"):
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown("##### 📚 Academic Credentials")
            f_branch = st.selectbox(
                "Branch",
                ["Computer Science", "Information Technology", "Electronics & Comm", "Electrical & Electronics", "Mechanical", "Civil"],
                index=["Computer Science", "Information Technology", "Electronics & Comm", "Electrical & Electronics", "Mechanical", "Civil"].index(sb_branch),
                key="f_branch"
            )
            f_cgpa = st.number_input("Undergrad CGPA (e.g. 8.45)", min_value=0.0, max_value=10.0, value=float(sb_cgpa), step=0.01, format="%.2f", key="f_cgpa")
            col_mf1, col_mf2 = st.columns(2)
            with col_mf1:
                f_tenth = st.number_input("10th %", 0.0, 100.0, float(sb_tenth), 0.5, format="%.1f", key="f_tenth")
            with col_mf2:
                f_twelfth = st.number_input("12th %", 0.0, 100.0, float(sb_twelfth), 0.5, format="%.1f", key="f_twelfth")
            f_backlogs = st.number_input("Active Backlogs / Arrears", 0, 10, int(sb_backlogs), 1, key="f_backlogs")
            
        with col_m2:
            st.markdown("##### 💻 Coding & Technical")
            f_dsa = st.number_input("DSA Solved (LeetCode / GFG)", 0, 1000, int(sb_dsa), 10, key="f_dsa")
            f_projects = st.number_input("Capstone Projects Count", 0, 10, int(sb_projects), 1, key="f_projects")
            f_hackathons = st.number_input("Hackathons Participated", 0, 10, int(sb_hackathons), 1, key="f_hackathons")
            f_role = st.selectbox("Target Role", list(ROLE_TAXONOMY.keys()), index=list(ROLE_TAXONOMY.keys()).index(sb_target_role), key="f_role")
            
        with col_m3:
            st.markdown("##### 💼 Experience & Behavioral")
            f_internships = st.number_input("Internships Count", 0, 6, int(sb_internships), 1, key="f_internships")
            f_certs = st.number_input("Certifications Count", 0, 10, int(sb_certs), 1, key="f_certs")
            f_aptitude = st.number_input("Aptitude Score (%)", 0.0, 100.0, float(sb_aptitude), 1.0, format="%.1f", key="f_aptitude")
            f_soft = st.number_input("Soft Skills Rating (1.0 - 5.0)", 1.0, 5.0, float(sb_soft_skills), 0.1, format="%.1f", key="f_soft")
            
        submitted_main = st.form_submit_button("🚀 Apply Custom Inputs & Recompute Analysis")
        if submitted_main:
            st.session_state["active_profile"] = {
                "Branch": f_branch,
                "CGPA": f_cgpa,
                "Tenth_Percentage": f_tenth,
                "Twelfth_Percentage": f_twelfth,
                "DSA_Problems_Solved": f_dsa,
                "Projects_Count": f_projects,
                "Internships_Count": f_internships,
                "Hackathons_Participated": f_hackathons,
                "Certifications_Count": f_certs,
                "Aptitude_Test_Score": f_aptitude,
                "Soft_Skills_Rating": f_soft,
                "Backlogs": f_backlogs,
                "target_role": f_role
            }
            st.success("✅ Custom profile updated! Recomputed readiness metrics below.")

# Resolve active profile
if "active_profile" in st.session_state and st.session_state.get("active_profile"):
    student_profile = st.session_state["active_profile"].copy()
    target_role = student_profile.pop("target_role", sb_target_role)
else:
    student_profile = {
        "Branch": sb_branch,
        "CGPA": sb_cgpa,
        "Tenth_Percentage": sb_tenth,
        "Twelfth_Percentage": sb_twelfth,
        "DSA_Problems_Solved": sb_dsa,
        "Projects_Count": sb_projects,
        "Internships_Count": sb_internships,
        "Hackathons_Participated": sb_hackathons,
        "Certifications_Count": sb_certs,
        "Aptitude_Test_Score": sb_aptitude,
        "Soft_Skills_Rating": sb_soft_skills,
        "Backlogs": sb_backlogs
    }
    target_role = sb_target_role

prediction = predict_student_readiness(student_profile)
pillar_scores = prediction["pillar_scores"]
overall_readiness = pillar_scores["Overall_Readiness"]
placement_prob = prediction["placement_probability"]

# Current Profile Summary Strip
st.markdown(f"""
<div style="background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 8px; padding: 8px 16px; margin-bottom: 16px; font-size: 0.88rem; color: #cbd5e1;">
    <b>Active Profile:</b> {student_profile['Branch']} | <b>CGPA:</b> {student_profile['CGPA']:.2f} | <b>10th/12th:</b> {student_profile['Tenth_Percentage']:.1f}% / {student_profile['Twelfth_Percentage']:.1f}% | <b>Backlogs:</b> {student_profile['Backlogs']} | <b>DSA:</b> {student_profile['DSA_Problems_Solved']} solved | <b>Internships:</b> {student_profile['Internships_Count']} | <b>Projects:</b> {student_profile['Projects_Count']}
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Tabs Navigation
# ---------------------------------------------------------
tab_readiness, tab_roadmap, tab_resume, tab_analytics, tab_quiz = st.tabs([
    "🎯 Readiness & Predictions",
    "🗺️ 90-Day Action Roadmap",
    "📄 Resume & ATS Matcher",
    "📊 Campus Cohort Analytics",
    "⚡ Diagnostic Quick Quiz"
])

# =========================================================
# TAB 1: READINESS & PREDICTIONS
# =========================================================
with tab_readiness:
    st.subheader("Candidate Assessment Overview")
    
    # 4 Top KPI Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-title">Overall Readiness Index</div>
            <div class="metric-card-value">{overall_readiness}%</div>
            <div class="metric-card-subtitle">
                {"🟢 High Placement Readiness" if overall_readiness >= 75 else ("🟡 Moderate Readiness" if overall_readiness >= 55 else "🔴 Urgent Intervention Required")}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-title">Placement Likelihood</div>
            <div class="metric-card-value">{placement_prob}%</div>
            <div class="metric-card-subtitle">
                ML Probability: {prediction['placement_probability']}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi3:
        tier_str = prediction["predicted_tier"]
        badge_class = "badge-tier1" if "Tier 1" in tier_str else ("badge-tier2" if "Tier 2" in tier_str else "badge-tier3")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-title">Target Placement Tier</div>
            <div style="margin-top: 8px;"><span class="{badge_class}">{tier_str}</span></div>
            <div class="metric-card-subtitle" style="margin-top: 10px;">Primary Recruiter Bracket</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-title">Estimated CTC Range</div>
            <div class="metric-card-value">{prediction['ctc_range']}</div>
            <div class="metric-card-subtitle">Median Expected: {prediction['predicted_ctc']} LPA</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.divider()
    
    # Visualizations Row: Gauge & Radar Chart
    chart_col1, chart_col2 = st.columns([1, 1])
    
    with chart_col1:
        st.markdown("#### 🎯 Placement Probability Gauge")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=placement_prob,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Likelihood of Campus Offer", 'font': {'size': 18, 'color': "#ffffff"}},
            delta={'reference': 50, 'increasing': {'color': "#10b981"}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#cbd5e1"},
                'bar': {'color': "#38bdf8", 'thickness': 0.3},
                'bgcolor': "#1e293b",
                'borderwidth': 1,
                'bordercolor': "#334155",
                'steps': [
                    {'range': [0, 50], 'color': '#ef4444'},
                    {'range': [50, 75], 'color': '#f59e0b'},
                    {'range': [75, 100], 'color': '#10b981'}
                ],
                'threshold': {
                    'line': {'color': "#ffffff", 'width': 3},
                    'thickness': 0.85,
                    'value': placement_prob
                }
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={'color': "#ffffff"},
            height=320,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        
    with chart_col2:
        st.markdown("#### 🕸️ 5-Pillar Competency Radar")
        categories = ["Academics", "DSA & Problem Solving", "Projects & Development", "Industry Exposure", "Aptitude & Soft Skills"]
        scores = [pillar_scores[cat] for cat in categories]
        benchmark = [80, 80, 80, 80, 80]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='Candidate Profile',
            line=dict(color='#38bdf8', width=2),
            fillcolor='rgba(56, 189, 248, 0.3)'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=benchmark + [benchmark[0]],
            theta=categories + [categories[0]],
            name='Tier-1 Benchmark (80%)',
            line=dict(color='#10b981', dash='dash', width=1.5)
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color="#94a3b8"),
                angularaxis=dict(color="#cbd5e1")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ffffff"),
            height=320,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
    # Second Row: Tier Probabilities & Feature Impact
    st.markdown("---")
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.markdown("#### 🏢 Company Tier Fitment Distribution")
        tier_data = prediction["tier_probabilities"]
        df_tier_chart = pd.DataFrame({
            "Tier": list(tier_data.keys()),
            "Probability (%)": list(tier_data.values())
        })
        fig_tier = px.bar(
            df_tier_chart,
            x="Tier",
            y="Probability (%)",
            text="Probability (%)",
            color="Tier",
            color_discrete_map={
                "Tier 1 (Product/MNC)": "#10b981",
                "Tier 2 (Tech Startup)": "#3b82f6",
                "Tier 3 (Service/Mass)": "#f59e0b"
            }
        )
        fig_tier.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_tier.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ffffff"),
            yaxis=dict(range=[0, 110], gridcolor="#334155"),
            xaxis=dict(color="#cbd5e1"),
            height=300,
            showlegend=False,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_tier, use_container_width=True)
        
    with row2_col2:
        st.markdown("#### ⚖️ Top Factors Influencing Your Placement")
        factors_df = pd.DataFrame(prediction["factors"][:6])
        fig_factors = px.bar(
            factors_df,
            x="Importance",
            y="Feature",
            orientation='h',
            text="Importance",
            color="Importance",
            color_continuous_scale="Viridis"
        )
        fig_factors.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_factors.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ffffff"),
            xaxis=dict(range=[0, max(factors_df["Importance"]) * 1.3], gridcolor="#334155"),
            yaxis=dict(autorange="reversed", color="#cbd5e1"),
            height=300,
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_factors, use_container_width=True)

    # What-If Career Simulator
    st.markdown("---")
    with st.expander("🔮 Interactive 'What-If' Career Simulator (Test Improvement Impact)", expanded=False):
        st.write("Adjust the sliders below to simulate how enhancing your skills changes your placement probability and expected salary:")
        sim_col1, sim_col2, sim_col3 = st.columns(3)
        with sim_col1:
            sim_dsa_add = st.slider("Extra DSA Problems to Solve", 0, 250, 50, step=25)
        with sim_col2:
            sim_intern_add = st.slider("Additional Internship", 0, 2, 1, step=1)
        with sim_col3:
            sim_backlog_clear = st.selectbox("Clear Backlogs to Zero?", ["Yes", "No"], index=0 if student_profile["Backlogs"] > 0 else 1)
            
        simulated_profile = student_profile.copy()
        simulated_profile["DSA_Problems_Solved"] = min(650, simulated_profile["DSA_Problems_Solved"] + sim_dsa_add)
        simulated_profile["Internships_Count"] = min(4, simulated_profile["Internships_Count"] + sim_intern_add)
        if sim_backlog_clear == "Yes":
            simulated_profile["Backlogs"] = 0
            
        sim_pred = predict_student_readiness(simulated_profile)
        
        prob_delta = round(sim_pred["placement_probability"] - placement_prob, 1)
        ctc_delta = round(sim_pred["predicted_ctc"] - prediction["predicted_ctc"], 1)
        
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Simulated Placement Likelihood", f"{sim_pred['placement_probability']}%", f"{prob_delta:+} %")
        sc2.metric("Simulated Expected CTC", f"{sim_pred['predicted_ctc']} LPA", f"{ctc_delta:+} LPA")
        sc3.metric("Simulated Company Tier", sim_pred["predicted_tier"])

# =========================================================
# TAB 2: SKILL GAP & 90-DAY ROADMAP
# =========================================================
with tab_roadmap:
    lowest_pillar, roadmap_phases = generate_custom_roadmap(pillar_scores, target_role)
    
    st.subheader(f"Personalized Placement Roadmap: {target_role}")
    st.info(f"💡 **AI Diagnostic Notice**: Your lowest competency pillar is **{lowest_pillar}** ({pillar_scores[lowest_pillar]}/100). The 90-day plan below prioritizes addressing this gap first to maximize recruitment conversion.")
    
    # Gap Comparison Table
    st.markdown("#### 📊 Target Role Competency Gap Breakdown")
    gap_data = []
    role_benchmarks = {
        "Academics": 75.0,
        "DSA & Problem Solving": 85.0 if "SDE" in target_role else 65.0,
        "Projects & Development": 80.0,
        "Industry Exposure": 70.0,
        "Aptitude & Soft Skills": 75.0
    }
    for k in ["Academics", "DSA & Problem Solving", "Projects & Development", "Industry Exposure", "Aptitude & Soft Skills"]:
        req = role_benchmarks.get(k, 75.0)
        curr = pillar_scores[k]
        diff = round(curr - req, 1)
        status = "✅ Meets Standard" if diff >= 0 else f"⚠️ Gap ({diff})"
        gap_data.append({
            "Competency Pillar": k,
            "Your Current Score": f"{curr}/100",
            "Target Requirement": f"{req}/100",
            "Status": status
        })
    st.table(pd.DataFrame(gap_data))
    
    st.markdown("---")
    st.markdown("#### 🗓️ Structured 90-Day Execution Plan")
    
    for phase_title, content in roadmap_phases.items():
        with st.expander(f"📌 {phase_title}", expanded=True):
            st.markdown(f"**{content['focus']}**")
            st.markdown("**Key Milestones & Deliverables:**")
            for m in content["milestones"]:
                st.checkbox(m, key=f"cb_{phase_title}_{m[:15]}")
            st.markdown("**Recommended Curated Resources:**")
            for r in content["resources"]:
                st.markdown(f"- 🔗 {r}")

# =========================================================
# TAB 3: RESUME & ATS MATCHER
# =========================================================
with tab_resume:
    st.subheader("📄 Resume ATS Keyword Matcher & Role Compatibility")
    st.markdown("Paste your resume content, technical skills, or capstone project descriptions below to analyze alignment with industry applicant tracking systems.")
    
    col_r1, col_r2 = st.columns([2, 1])
    with col_r1:
        ats_role = st.selectbox("Select Target ATS Role", list(ROLE_TAXONOMY.keys()), index=list(ROLE_TAXONOMY.keys()).index(target_role))
    with col_r2:
        st.write("")
        st.write("")
        sample_btn = st.button("📋 Load Sample SDE Resume Text")
        
    default_resume_text = """John Doe - Software Engineering Student
GitHub: github.com/johndoe | LinkedIn: linkedin.com/in/johndoe

Technical Skills:
- Languages: Python, Java, C++, JavaScript, SQL
- Core Fundamentals: Data Structures, Algorithms, Object Oriented Programming (OOP), DBMS, Operating Systems
- Tools & Frameworks: Git, GitHub, React, Node.js, Express, Docker, REST API

Projects:
1. Distributed E-Commerce Microservices Platform:
   - Engineered high-throughput REST APIs handling 10,000+ requests per minute with Redis caching.
   - Designed normalized PostgreSQL DBMS schema ensuring ACID compliance.
   - Deployed on AWS ECS with Docker containers and automated CI/CD pipeline.

2. Algorithmic Trading Backtester:
   - Implemented custom Data Structures and Graph Algorithms for order matching engine.
   - Reduced latency by 45% using optimized C++ memory management.
"""
    if sample_btn:
        resume_input = st.text_area("Resume Text Content", value=default_resume_text, height=260)
    else:
        resume_input = st.text_area(
            "Resume Text Content",
            value="",
            placeholder="Paste your resume sections (Skills, Projects, Experience, Summary) here...",
            height=260
        )
        
    if resume_input:
        ats_result = analyze_resume_text(resume_input, ats_role)
        
        score = ats_result["score"]
        st.markdown(f"### ATS Match Score: **{score}%**")
        st.progress(score / 100.0)
        
        ats_col1, ats_col2 = st.columns(2)
        with ats_col1:
            st.markdown("#### ✅ Detected Core Required Skills")
            if ats_result["matched_required"]:
                for s in ats_result["matched_required"]:
                    st.markdown(f"<span class='skill-chip chip-matched'>✓ {s}</span>", unsafe_allow_html=True)
            else:
                st.write("None detected.")
                
            st.markdown("#### ❌ Missing Core Required Skills")
            if ats_result["missing_required"]:
                for s in ats_result["missing_required"]:
                    st.markdown(f"<span class='skill-chip chip-missing'>✗ {s}</span>", unsafe_allow_html=True)
            else:
                st.write("All core required keywords detected!")
                
        with ats_col2:
            st.markdown("#### 🌟 Detected High-Value / Modern Skills")
            if ats_result["matched_optional"]:
                for s in ats_result["matched_optional"]:
                    st.markdown(f"<span class='skill-chip chip-opt-matched'>✓ {s}</span>", unsafe_allow_html=True)
            else:
                st.write("None detected.")
                
            st.markdown("#### 💡 Recommended High-Value Additions")
            if ats_result["missing_optional"]:
                for s in ats_result["missing_optional"]:
                    st.markdown(f"<span class='skill-chip chip-opt-missing'>+ {s}</span>", unsafe_allow_html=True)
            else:
                st.write("All modern high-value tools detected!")
                
        st.markdown("---")
        st.markdown("#### 🎯 Actionable ATS Optimization Recommendations")
        for rec in ats_result["recommendations"]:
            st.markdown(f"- {rec}")
    else:
        st.info("👆 Paste your resume text or click **'Load Sample SDE Resume Text'** to see instant keyword analysis.")

# =========================================================
# TAB 4: CAMPUS COHORT ANALYTICS
# =========================================================
with tab_analytics:
    st.subheader("📊 Campus Placement Cohort Analytics (1,500 Engineering Students)")
    st.markdown("Explore historical hiring patterns, placement conversion rates, and salary distributions across branches.")
    
    # Cohort Top Metrics
    total_students = len(df_cohort)
    placed_students = df_cohort["Placed"].sum()
    overall_rate = round((placed_students / total_students) * 100, 1)
    avg_ctc = round(df_cohort[df_cohort["Placed"] == 1]["CTC_Offered_LPA"].mean(), 2)
    max_ctc = round(df_cohort["CTC_Offered_LPA"].max(), 1)
    
    cm1, cm2, cm3, cm4 = st.columns(4)
    cm1.metric("Total Batch Students", f"{total_students:,}")
    cm2.metric("Overall Placement Rate", f"{overall_rate}%")
    cm3.metric("Average Placed CTC", f"{avg_ctc} LPA")
    cm4.metric("Highest Package Offered", f"{max_ctc} LPA")
    
    st.markdown("---")
    ca_col1, ca_col2 = st.columns(2)
    
    with ca_col1:
        st.markdown("#### 🏫 Branch-wise Placement Clearance Rate")
        branch_stats = df_cohort.groupby("Branch")["Placed"].mean().reset_index()
        branch_stats["Placement Rate (%)"] = round(branch_stats["Placed"] * 100, 1)
        fig_branch = px.bar(
            branch_stats.sort_values(by="Placement Rate (%)", ascending=False),
            x="Branch",
            y="Placement Rate (%)",
            text="Placement Rate (%)",
            color="Placement Rate (%)",
            color_continuous_scale="Blues"
        )
        fig_branch.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_branch.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ffffff"),
            yaxis=dict(range=[0, 100], gridcolor="#334155"),
            xaxis=dict(color="#cbd5e1"),
            height=320,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_branch, use_container_width=True)
        
    with ca_col2:
        st.markdown("#### 💻 DSA Solved vs CTC Offered (LPA)")
        placed_only = df_cohort[df_cohort["Placed"] == 1]
        fig_scatter = px.scatter(
            placed_only,
            x="DSA_Problems_Solved",
            y="CTC_Offered_LPA",
            color="Company_Tier",
            hover_data=["CGPA", "Branch", "Internships_Count"],
            color_discrete_map={
                "Tier 1 (Product/MNC)": "#10b981",
                "Tier 2 (Tech Startup/Mid-Corp)": "#3b82f6",
                "Tier 3 (Service/Mass Recruiter)": "#f59e0b"
            }
        )
        fig_scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ffffff"),
            xaxis=dict(title="DSA Problems Solved", gridcolor="#334155"),
            yaxis=dict(title="CTC Offered (LPA)", gridcolor="#334155"),
            height=320,
            legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    ca_col3, ca_col4 = st.columns(2)
    with ca_col3:
        st.markdown("#### ⚠️ Impact of Active Backlogs on Placement Clearance")
        backlog_stats = df_cohort.groupby("Backlogs")["Placed"].mean().reset_index()
        backlog_stats["Placement Rate (%)"] = round(backlog_stats["Placed"] * 100, 1)
        fig_backlog = px.bar(
            backlog_stats,
            x="Backlogs",
            y="Placement Rate (%)",
            text="Placement Rate (%)",
            color="Placement Rate (%)",
            color_continuous_scale="Reds_r"
        )
        fig_backlog.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_backlog.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ffffff"),
            yaxis=dict(range=[0, 100], gridcolor="#334155"),
            xaxis=dict(title="Number of Active Backlogs", tickmode="linear", color="#cbd5e1"),
            height=300,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_backlog, use_container_width=True)
        
    with ca_col4:
        st.markdown("#### 📈 CGPA Distribution: Placed vs Unplaced")
        fig_box = px.histogram(
            df_cohort,
            x="CGPA",
            color="Placed",
            barmode="overlay",
            nbins=25,
            color_discrete_map={1: "#10b981", 0: "#ef4444"},
            labels={"Placed": "Placement Status"}
        )
        fig_box.for_each_trace(lambda t: t.update(name="Placed" if t.name == "1" else "Unplaced"))
        fig_box.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#ffffff"),
            xaxis=dict(title="Undergrad CGPA", gridcolor="#334155"),
            yaxis=dict(title="Student Count", gridcolor="#334155"),
            height=300,
            legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_box, use_container_width=True)

    # Data Table View & CSV Download
    with st.expander("🔍 Explore Raw Placement Dataset"):
        st.dataframe(df_cohort.head(100), use_container_width=True)
        csv_data = df_cohort.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Placement Dataset (CSV)",
            data=csv_data,
            file_name="placement_data.csv",
            mime="text/csv"
        )

# =========================================================
# TAB 5: DIAGNOSTIC QUICK QUIZ
# =========================================================
with tab_quiz:
    st.subheader("⚡ 5-Question Diagnostic Readiness Quiz")
    st.markdown("Test your command over core recruitment domains: DSA, Operating Systems, DBMS, Networks, and Quantitative Aptitude.")
    
    user_answers = {}
    with st.form("quiz_form"):
        for q in DIAGNOSTIC_QUIZ:
            st.markdown(f"**Q{q['id']}. [{q['category']}]** {q['question']}")
            user_answers[q["id"]] = st.radio(
                "Select your answer:",
                options=q["options"],
                key=f"quiz_q_{q['id']}",
                index=None
            )
            st.write("")
            
        submitted = st.form_submit_button("📝 Submit Diagnostic Quiz & Calibrate Score")
        
    if submitted:
        correct_count = 0
        st.markdown("### Quiz Results & Answer Key")
        for q in DIAGNOSTIC_QUIZ:
            ans = user_answers.get(q["id"])
            if ans == q["answer"]:
                correct_count += 1
                st.success(f"**Q{q['id']} [Correct]**: {q['question']}\n\n**Your Answer**: {ans}\n\n*Explanation*: {q['explanation']}")
            else:
                st.error(f"**Q{q['id']} [Incorrect]**: {q['question']}\n\n**Your Answer**: {ans or 'Not answered'} | **Correct Answer**: {q['answer']}\n\n*Explanation*: {q['explanation']}")
                
        quiz_pct = (correct_count / len(DIAGNOSTIC_QUIZ)) * 100
        st.info(f"🎯 **Your Score: {correct_count}/{len(DIAGNOSTIC_QUIZ)} ({quiz_pct:.0f}%)**")
        if quiz_pct >= 80:
            st.balloons()
            st.success("🌟 Excellent technical foundation! You are well-calibrated for Tier 1 and Tier 2 technical screening rounds.")
        elif quiz_pct >= 60:
            st.warning("⚠️ Fair performance. Review Core CS fundamentals (OS, DBMS, Networking) to boost your technical MCQ clearance rate.")
        else:
            st.error("🚨 Critical gap in fundamentals detected. Prioritize Phase 1 of your personalized 90-day roadmap.")

