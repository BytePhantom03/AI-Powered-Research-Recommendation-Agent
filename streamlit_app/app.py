import streamlit as st
import mimetypes

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
import requests
import time
import json
import os

API_URL = os.environ.get("API_URL", "http://backend:8000/v1")

st.set_page_config(
    page_title="AI Research Agent — Company Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────── CUSTOM CSS ───────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-primary: #0a0e1a;
    --bg-card: #111827;
    --bg-card-hover: #1a2235;
    --accent: #6366f1;
    --accent-light: #818cf8;
    --accent-glow: rgba(99,102,241,.25);
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --border: #1e293b;
    --severity-high: #ef4444;
    --severity-medium: #f59e0b;
    --severity-low: #22c55e;
    --impact-high: #6366f1;
    --impact-medium: #8b5cf6;
    --impact-low: #a78bfa;
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}
.stApp {
    background: linear-gradient(160deg, #0a0e1a 0%, #0f1629 50%, #0a0e1a 100%);
}

/* ── Hero section ── */
.hero-container {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, var(--accent), #8b5cf6);
    color: white;
    font-size: .7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .12em;
    padding: .35rem 1rem;
    border-radius: 100px;
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #f1f5f9, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.15;
    margin-bottom: .6rem;
}
.hero-sub {
    color: var(--text-secondary);
    font-size: 1.05rem;
    max-width: 600px;
    margin: 0 auto 1.5rem;
    line-height: 1.5;
}

/* ── Cards ── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.25rem 1.4rem;
    transition: border-color .2s, box-shadow .2s;
}
.metric-card:hover {
    border-color: var(--accent);
    box-shadow: 0 0 20px var(--accent-glow);
}
.metric-label {
    color: var(--text-secondary);
    font-size: .75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-bottom: .3rem;
}
.metric-value {
    color: var(--text-primary);
    font-size: 1.25rem;
    font-weight: 700;
}

/* ── Section cards ── */
.section-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color .2s, box-shadow .2s;
}
.section-card:hover {
    border-color: var(--accent);
    box-shadow: 0 0 24px var(--accent-glow);
}
.section-title {
    color: var(--accent-light);
    font-size: 1.35rem;
    font-weight: 700;
    margin-bottom: .6rem;
}
.section-body {
    color: var(--text-secondary);
    font-size: .95rem;
    line-height: 1.7;
}

/* ── Severity / Impact chips ── */
.chip {
    display: inline-block;
    padding: .2rem .7rem;
    border-radius: 100px;
    font-size: .72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .06em;
}
.chip-high   { background: rgba(239,68,68,.15); color: #ef4444; }
.chip-medium { background: rgba(245,158,11,.15); color: #f59e0b; }
.chip-low    { background: rgba(34,197,94,.15);  color: #22c55e; }
.chip-impact-high   { background: rgba(99,102,241,.15); color: #6366f1; }
.chip-impact-medium { background: rgba(139,92,246,.15); color: #8b5cf6; }
.chip-impact-low    { background: rgba(167,139,250,.15); color: #a78bfa; }
.chip-category {
    background: rgba(99,102,241,.1);
    color: var(--accent-light);
}

/* ── Item cards (challenges, opportunities) ── */
.item-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: .8rem;
    transition: transform .15s, border-color .2s, box-shadow .2s;
}
.item-card:hover {
    border-color: var(--accent);
    box-shadow: 0 4px 20px var(--accent-glow);
    transform: translateY(-2px);
}
.item-title {
    color: var(--text-primary);
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: .45rem;
}
.item-meta {
    display: flex;
    gap: .5rem;
    flex-wrap: wrap;
    margin-bottom: .5rem;
}
.item-reasoning {
    color: var(--text-secondary);
    font-size: .88rem;
    line-height: 1.6;
}

/* ── Bullet items ── */
.bullet-item {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: .85rem 1.2rem;
    margin-bottom: .5rem;
    color: var(--text-secondary);
    font-size: .92rem;
    line-height: 1.5;
    transition: border-color .2s;
}
.bullet-item:hover { border-color: var(--accent); }
.bullet-dot {
    display: inline-block;
    width: 6px; height: 6px;
    background: var(--accent);
    border-radius: 50%;
    margin-right: .6rem;
    vertical-align: middle;
}

/* ── CEO Pitch card ── */
.pitch-card {
    background: linear-gradient(135deg, rgba(99,102,241,.08), rgba(139,92,246,.08));
    border: 1px solid rgba(99,102,241,.25);
    border-radius: 14px;
    padding: 2rem;
    color: var(--text-primary);
    font-size: .95rem;
    line-height: 1.8;
}

/* ── Sub-section heading ── */
.sub-heading {
    color: var(--accent-light);
    font-size: .85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin: 1.2rem 0 .6rem;
}

/* ── Progress container ── */
.progress-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 2rem;
    text-align: center;
    margin: 1rem 0;
}
.progress-title {
    color: var(--text-primary);
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: .4rem;
}
.progress-sub {
    color: var(--text-secondary);
    font-size: .85rem;
}

/* ── Sidebar tweaks ── */
section[data-testid="stSidebar"] {
    background: #0c1021 !important;
    border-right: 1px solid var(--border);
}

/* ── Download buttons ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, var(--accent), #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: .6rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: .85rem !important;
    transition: opacity .2s !important;
}
.stDownloadButton > button:hover {
    opacity: .85 !important;
}

/* ── Hide default Streamlit branding ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--bg-card);
    border-radius: 12px;
    padding: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: var(--text-secondary);
    font-weight: 600;
    font-size: .82rem;
    padding: .5rem 1rem;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: white !important;
}

/* ── Streamlit button override ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: .65rem 2rem !important;
    font-weight: 600 !important;
    font-size: .9rem !important;
    letter-spacing: .02em !important;
    transition: opacity .2s, transform .15s !important;
}
.stButton > button:hover {
    opacity: .9 !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Text input override ── */
.stTextInput > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    padding: .6rem 1rem !important;
    font-size: .9rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────── HELPER FUNCTIONS ───────────────────────────

def severity_chip(sev):
    s = (sev or "").upper()
    cls = "chip-high" if s == "HIGH" else ("chip-medium" if s == "MEDIUM" else "chip-low")
    return f'<span class="chip {cls}">{s}</span>'

def impact_chip(imp):
    s = (imp or "").upper()
    cls = "chip-impact-high" if s == "HIGH" else ("chip-impact-medium" if s == "MEDIUM" else "chip-impact-low")
    return f'<span class="chip {cls}">{s}</span>'

def category_chip(cat):
    return f'<span class="chip chip-category">{cat}</span>'

def render_metric(label, value):
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

def render_bullet(text):
    return f'<div class="bullet-item"><span class="bullet-dot"></span>{text}</div>'

# ─────────────────────────── SIDEBAR ───────────────────────────

with st.sidebar:
    st.markdown("### 🔑 API Configuration")
    st.caption("Keys are sent directly to the backend and never stored.")
    gemini_key = st.text_input("Gemini API Key", type="password", placeholder="AIzaSy...")
    tavily_key = st.text_input("Tavily API Key", type="password", placeholder="tvly-...")
    groq_key = st.text_input("Groq API Key (Optional Fallback)", type="password", placeholder="gsk_...")
    st.divider()
    st.markdown("### ℹ️ About")
    st.caption(
        "This tool uses **Gemini 2.5 Flash** (with automatic fallback to Groq Llama 3) for AI analysis "
        "and **Tavily** for live web research to generate comprehensive company intelligence reports in under 3 minutes."
    )
    st.divider()
    st.caption("Built with ❤️ using FastAPI, LangChain & Streamlit")

# ─────────────────────────── HERO ───────────────────────────

st.markdown("""
<div class="hero-container">
    <div class="hero-badge">AI-Powered Intelligence</div>
    <div class="hero-title">Company Research Agent</div>
    <div class="hero-sub">
        Generate comprehensive business intelligence reports with AI. 
        Enter any company name and get a full analysis in minutes.
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────── INPUT ───────────────────────────

col_input, col_btn = st.columns([4, 1])
with col_input:
    company_name = st.text_input(
        "Company Name",
        placeholder="e.g. Unada Labs, Adani Realty, Infosys...",
        label_visibility="collapsed",
    )
with col_btn:
    generate_clicked = st.button("🚀 Generate Report", use_container_width=True)

# ─────────────────────────── GENERATION FLOW ───────────────────────────

if generate_clicked:
    if not gemini_key or not tavily_key:
        st.error("⚠️ Please enter both **Gemini** and **Tavily** API keys in the sidebar.")
        st.stop()
    if len(company_name) < 2:
        st.error("⚠️ Company name must be at least 2 characters.")
        st.stop()

    # Kick off report
    with st.spinner("Initializing research pipeline..."):
        try:
            response = requests.post(
                f"{API_URL}/reports",
                json={
                    "company_name": company_name,
                    "options": {
                        "api_keys": {
                            "gemini": gemini_key,
                            "tavily": tavily_key,
                            "groq": groq_key,
                        }
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            report_id = data["report_id"]
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to start report generation: {e}")
            st.stop()

    status_placeholder = st.empty()
    progress_bar = st.progress(0)

    # Poll for status
    while True:
        try:
            status_res = requests.get(f"{API_URL}/reports/{report_id}/status")
            status_res.raise_for_status()
            status_data = status_res.json()
            status = status_data["status"]

            if status == "PENDING":
                status_placeholder.markdown(
                    '<div class="progress-container">'
                    '<div class="progress-title">⏳ Queued — waiting to start...</div>'
                    '<div class="progress-sub">Your report will begin processing shortly.</div>'
                    "</div>",
                    unsafe_allow_html=True,
                )
            elif status in ("RESEARCHING", "PROCESSING"):
                prog = status_data.get("progress")
                if prog:
                    pct = prog.get("percentage", 0)
                    task = prog.get("current_task", "Processing...")
                    progress_bar.progress(pct)
                    status_placeholder.markdown(
                        f'<div class="progress-container">'
                        f'<div class="progress-title">🔬 {task}</div>'
                        f'<div class="progress-sub">Progress: {pct}% complete</div>'
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    status_placeholder.markdown(
                        '<div class="progress-container">'
                        f'<div class="progress-title">🔄 {status.title()}...</div>'
                        '<div class="progress-sub">Working on your report...</div>'
                        "</div>",
                        unsafe_allow_html=True,
                    )
            elif status == "COMPLETE":
                progress_bar.progress(100)
                status_placeholder.success("✅ Report generated successfully!")
                break
            elif status == "FAILED":
                status_placeholder.error("❌ Report generation failed. Please check your API keys and try again.")
                st.stop()

        except requests.exceptions.RequestException as e:
            status_placeholder.warning(f"⚠️ Connection error: {e}. Retrying...")

        time.sleep(3)

    # ─────────────────────────── FETCH & DISPLAY REPORT ───────────────────────────

    try:
        report_res = requests.get(f"{API_URL}/reports/{report_id}")
        report_res.raise_for_status()
        report_data = report_res.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch report: {e}")
        st.stop()

    company = report_data.get("company", {})
    sections = report_data.get("sections", {})
    overview = sections.get("company_overview") or {}
    biz = sections.get("business_info") or {}
    chal = sections.get("challenges") or {}
    ai_opps = sections.get("ai_opportunities") or {}
    pitch = sections.get("ceo_pitch") or {}

    # ── Report Header ──
    st.markdown(f"""
    <div class="section-card" style="text-align:center; border-color: var(--accent); margin-top: 1rem;">
        <div style="font-size:.8rem; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:var(--accent-light); margin-bottom:.4rem;">Intelligence Report</div>
        <div style="font-size:2rem; font-weight:800; color:var(--text-primary);">{company.get('name', company_name)}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick metrics ──
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(render_metric("Industry", overview.get("industry", "N/A")), unsafe_allow_html=True)
    with m2:
        st.markdown(render_metric("Scale", overview.get("scale", "N/A")), unsafe_allow_html=True)
    with m3:
        st.markdown(render_metric("Confidence", f"{overview.get('confidence_score', 'N/A')}"), unsafe_allow_html=True)
    with m4:
        geo = overview.get("geographic_presence", [])
        st.markdown(render_metric("Locations", str(len(geo)) if geo else "N/A"), unsafe_allow_html=True)

    st.markdown("<div style='height: .8rem'></div>", unsafe_allow_html=True)

    # ── Tabs ──
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Overview", "💼 Business Info", "⚠️ Challenges", "🤖 AI Opportunities", "🎯 CEO Pitch"
    ])

    # ── TAB 1: Overview ──
    with tab1:
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">Company Overview</div>
            <div class="section-body">{overview.get('summary', 'No data available.')}</div>
        </div>
        """, unsafe_allow_html=True)

        if geo:
            st.markdown('<div class="sub-heading">🌍 Geographic Presence</div>', unsafe_allow_html=True)
            cols = st.columns(min(len(geo), 4))
            for i, loc in enumerate(geo):
                with cols[i % min(len(geo), 4)]:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align:center; padding:.8rem;">
                        <div class="metric-value" style="font-size:.9rem;">{loc}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── TAB 2: Business Info ──
    with tab2:
        if biz.get("offerings"):
            st.markdown('<div class="sub-heading">🏷️ Core Offerings</div>', unsafe_allow_html=True)
            for item in biz["offerings"]:
                st.markdown(render_bullet(item), unsafe_allow_html=True)

        if biz.get("developments"):
            st.markdown('<div class="sub-heading">📰 Recent Developments</div>', unsafe_allow_html=True)
            for item in biz["developments"]:
                st.markdown(render_bullet(item), unsafe_allow_html=True)

        if biz.get("expansion_plans"):
            st.markdown('<div class="sub-heading">🚀 Expansion Plans</div>', unsafe_allow_html=True)
            for item in biz["expansion_plans"]:
                st.markdown(render_bullet(item), unsafe_allow_html=True)

    # ── TAB 3: Challenges ──
    with tab3:
        items = chal.get("items", [])
        if items:
            for item in items:
                sev = severity_chip(item.get("severity"))
                cat = category_chip(item.get("category", ""))
                st.markdown(f"""
                <div class="item-card">
                    <div class="item-title">{item.get('challenge', 'N/A')}</div>
                    <div class="item-meta">{cat} {sev}</div>
                    <div class="item-reasoning">{item.get('reasoning', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No challenges identified.")

    # ── TAB 4: AI Opportunities ──
    with tab4:
        items = ai_opps.get("items", [])
        if items:
            for item in items:
                imp = impact_chip(item.get("impact"))
                eff = severity_chip(item.get("effort"))
                cat = category_chip(item.get("category", ""))
                st.markdown(f"""
                <div class="item-card">
                    <div class="item-title">{item.get('opportunity', 'N/A')}</div>
                    <div class="item-meta">{cat} {imp} <span class="chip chip-category">Effort: {(item.get('effort') or 'N/A').upper()}</span></div>
                    <div class="item-reasoning">{item.get('rationale', '')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No AI opportunities identified.")

    # ── TAB 5: CEO Pitch ──
    with tab5:
        pitch_content = pitch.get("content", "No pitch generated.")
        st.markdown(f"""
        <div class="pitch-card">
            {pitch_content}
        </div>
        """, unsafe_allow_html=True)

    # ── Download Section ──
    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sub-heading">📥 Export Report</div>', unsafe_allow_html=True)

    dl1, dl2, dl_spacer = st.columns([1, 1, 2])
    with dl1:
        st.download_button(
            label="⬇️ Download JSON",
            data=json.dumps(report_data, indent=2, default=str),
            file_name=f"{company.get('canonical_name', 'report')}_report.json",
            mime="application/json",
            use_container_width=True,
        )
    with dl2:
        try:
            pdf_res = requests.get(f"{API_URL}/reports/{report_id}/pdf")
            if pdf_res.status_code == 200:
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_res.content,
                    file_name=f"{company.get('canonical_name', 'report')}_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.error("PDF generation failed.")
        except Exception as e:
            st.error(f"PDF fetch error: {e}")
