import streamlit as st
import os
import time
from core.parser           import ResumeParser
from core.preprocessor     import TextPreprocessor
from core.ats_checker      import ATSChecker
from core.skill_extractor  import SkillExtractor
from core.semantic_matcher import SemanticMatcher
from core.gap_analyzer     import GapAnalyzer
from agents.crew_manager   import ResumifyCrewManager
from utils.helpers         import score_color, format_skill_badge, clean_markdown

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Resumify — Your Job Mate!",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Space+Grotesk:wght@400;600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a0a0f;
    color: #e8e8f0;
  }

  /* ── Hero Banner ── */
  .hero {
    background: linear-gradient(135deg, #1a0533 0%, #0d1b4b 50%, #001a33 100%);
    border: 1px solid #3a1f6e;
    border-radius: 20px;
    padding: 40px;
    text-align: center;
    margin-bottom: 28px;
    box-shadow: 0 0 60px rgba(120,60,255,0.25);
  }
  .hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
  }
  .hero p {
    color: #94a3b8;
    font-size: 1.1rem;
    margin-top: 10px;
  }

  /* ── Score Cards ── */
  .score-card {
    background: linear-gradient(145deg, #111827, #1e1b4b);
    border: 1px solid #312e81;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(99,102,241,0.2);
    transition: transform .2s;
  }
  .score-card:hover { transform: translateY(-4px); }
  .score-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    margin: 0;
    line-height: 1;
  }
  .score-label {
    color: #94a3b8;
    font-size: .85rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 8px;
  }

  /* ── Section Headers ── */
  .section-header {
    background: linear-gradient(90deg, #1e1b4b, transparent);
    border-left: 4px solid #818cf8;
    padding: 12px 20px;
    border-radius: 0 12px 12px 0;
    margin: 24px 0 16px;
  }
  .section-header h2 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #c7d2fe;
    margin: 0;
  }

  /* ── Skill Pills ── */
  .skill-pill-found {
    display: inline-block;
    background: rgba(0,200,81,0.15);
    color: #4ade80;
    border: 1px solid #166534;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    margin: 3px;
  }
  .skill-pill-missing {
    display: inline-block;
    background: rgba(255,68,68,0.12);
    color: #f87171;
    border: 1px solid #7f1d1d;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    margin: 3px;
  }
  .skill-pill-must {
    display: inline-block;
    background: rgba(239,68,68,0.15);
    color: #fca5a5;
    border: 1px solid #991b1b;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
    margin: 3px;
  }
  .skill-pill-good {
    display: inline-block;
    background: rgba(251,191,36,0.12);
    color: #fde68a;
    border: 1px solid #92400e;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
    margin: 3px;
  }
  .skill-pill-bonus {
    display: inline-block;
    background: rgba(56,189,248,0.12);
    color: #7dd3fc;
    border: 1px solid #0c4a6e;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
    margin: 3px;
  }

  /* ── Agent Output Cards ── */
  .agent-card {
    background: linear-gradient(145deg, #0f172a, #1e293b);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  }
  .agent-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  /* ── Progress Bar ── */
  .progress-bar-bg {
    background: #1e293b;
    border-radius: 10px;
    height: 12px;
    overflow: hidden;
    margin: 8px 0;
  }
  .progress-bar-fill {
    height: 100%;
    border-radius: 10px;
    transition: width 0.8s ease;
  }

  /* ── Info Box ── */
  .info-box {
    background: rgba(99,102,241,0.1);
    border: 1px solid #4338ca;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
    color: #c7d2fe;
    font-size: .95rem;
  }

  /* ── Streamlit overrides ── */
  .stButton > button {
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 28px;
    font-weight: 700;
    font-size: 1rem;
    width: 100%;
    transition: all .2s;
    box-shadow: 0 4px 15px rgba(124,58,237,0.4);
  }
  .stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(124,58,237,0.6);
  }
  .stFileUploader {
    background: #111827;
    border: 2px dashed #374151;
    border-radius: 12px;
    padding: 12px;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #94a3b8;
    font-weight: 600;
  }
  .stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.2);
    color: #818cf8;
    border-bottom: 2px solid #818cf8;
  }
  div[data-testid="stMetric"] {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 16px;
  }
  .stSidebar {
    background: #060610;
    border-right: 1px solid #1e293b;
  }
  /* Scrollbar */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #0a0a0f; }
  ::-webkit-scrollbar-thumb { background: #312e81; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Hero Banner ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🚀 Resumify — Your Job Mate!</h1>
  <p>AI-powered resume analysis · ATS scoring · Skill gap detection · Career roadmaps</p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0;">
      <div style="font-size:2.5rem;">🚀</div>
      <div style="font-family:'Space Grotesk',sans-serif;font-size:1.2rem;
                  font-weight:700;color:#a78bfa;">Resumify</div>
      <div style="color:#64748b;font-size:.8rem;">Your AI Job Mate</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📌 How It Works")
    steps = [
        ("1️⃣", "Upload your resume (PDF/DOCX)"),
        ("2️⃣", "Paste the job description"),
        ("3️⃣", "Click **Analyze**"),
        ("4️⃣", "Get ATS score, skill gaps & roadmap"),
    ]
    for icon, text in steps:
        st.markdown(f"**{icon}** {text}")

    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    threshold = st.slider(
        "Semantic Match Threshold",
        min_value=0.30, max_value=0.70,
        value=0.42, step=0.02,
        help="Lower = more lenient matching. Higher = stricter."
    )

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;color:#475569;font-size:.75rem;margin-top:20px;">
      Built with ❤️ using<br>CrewAI · Streamlit · OpenRouter<br>
      sentence-transformers · DuckDuckGo
    </div>
    """, unsafe_allow_html=True)


# ── Input Section ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown("""
    <div class="section-header">
      <h2>📄 Upload Your Resume</h2>
    </div>
    """, unsafe_allow_html=True)
    resume_file = st.file_uploader(
        "Drop your resume here",
        type=["pdf", "docx"],
        key="resume_uploader",
        help="Supports PDF and DOCX formats"
    )
    if resume_file:
        st.success(f"✅ Loaded: **{resume_file.name}** "
                   f"({round(resume_file.size/1024, 1)} KB)")

with col_right:
    st.markdown("""
    <div class="section-header">
      <h2>📋 Paste Job Description</h2>
    </div>
    """, unsafe_allow_html=True)
    jd_text_input = st.text_area(
        "Paste the full job description here",
        height=220,
        placeholder="Copy and paste the entire job description from LinkedIn, "
                    "Indeed, company website, etc.",
        key="jd_input"
    )
    if jd_text_input:
        wc = len(jd_text_input.split())
        st.caption(f"📊 {wc} words detected")

st.markdown("<br>", unsafe_allow_html=True)

# ── Analyze Button ────────────────────────────────────────────────────────────
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    analyze_btn = st.button("🔍 Analyze My Resume", use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# ── MAIN ANALYSIS PIPELINE ───────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════
if analyze_btn:
    # Validation
    if not resume_file:
        st.error("⚠️ Please upload your resume (PDF or DOCX).")
        st.stop()
    if not jd_text_input.strip():
        st.error("⚠️ Please paste a job description.")
        st.stop()
    if not os.getenv("OPENROUTER_API_KEY"):
        st.error("⚠️ OPENROUTER_API_KEY not found in .env file.")
        st.stop()

    # ── Override threshold from sidebar ──────────────────────────────────────
    import config.settings as cfg
    cfg.SEMANTIC_THRESHOLD = threshold

    # ── Pipeline ──────────────────────────────────────────────────────────────
    overall_progress = st.progress(0, text="Starting analysis…")
    status_text      = st.empty()

    try:
        # STAGE 1 — Parse
        status_text.markdown("**Stage 1/6 — 📄 Parsing resume…**")
        parser    = ResumeParser()
        file_path = parser.save_uploaded_file(resume_file)
        parsed    = parser.parse(file_path)
        overall_progress.progress(15, text="Parsing complete")
        time.sleep(0.3)

        # STAGE 2 — Preprocess
        status_text.markdown("**Stage 2/6 — 🧹 Preprocessing text…**")
        preprocessor  = TextPreprocessor()
        resume_proc   = preprocessor.preprocess(parsed["raw_text"])
        jd_proc       = preprocessor.preprocess_jd(jd_text_input)
        overall_progress.progress(25, text="Preprocessing complete")
        time.sleep(0.3)

        # STAGE 3 — ATS Check
        status_text.markdown("**Stage 3/6 — 📊 Running ATS analysis…**")
        ats_checker = ATSChecker()
        ats_result  = ats_checker.analyze(
            parsed["raw_text"],
            parsed["format"],
            resume_proc["sections"]
        )
        overall_progress.progress(40, text="ATS analysis complete")
        time.sleep(0.3)

        # STAGE 4 — Skill Extraction + Semantic Matching
        status_text.markdown("**Stage 4/6 — 🤖 Extracting skills from JD with AI…**")
        extractor    = SkillExtractor()
        jd_extracted = extractor.extract_from_jd(jd_proc["full_text"])
        jd_skills    = extractor.get_all_jd_skills(jd_extracted)
        overall_progress.progress(55, text="Skill extraction complete")

        # ── Debug: show what was extracted (helps diagnose issues) ──
        if not jd_skills:
            st.warning(
                "⚠️ No skills were extracted from the job description. "
                "This usually means the LLM response failed to parse. "
                "Check that your OPENROUTER_API_KEY is valid and the model is responding."
            )
        else:
            st.info(
                f"✅ Extracted **{len(jd_skills)} skills** from JD for role: "
                f"**{jd_extracted.get('job_title', 'Unknown')}**"
            )

        status_text.markdown("**Stage 4/6 — 🔍 Running semantic skill matching…**")
        matcher         = SemanticMatcher()
        semantic_result = matcher.match(resume_proc["normalized_text"], jd_skills)
        doc_similarity  = matcher.overall_similarity(
            resume_proc["normalized_text"], jd_proc["full_text"]
        )
        overall_progress.progress(68, text="Semantic matching complete")
        time.sleep(0.3)

        # STAGE 5 — Gap Analysis
        status_text.markdown("**Stage 5/6 — 🔎 Analyzing skill gaps…**")
        gap_analyzer = GapAnalyzer()
        gap_analysis = gap_analyzer.analyze(
            semantic_result["missing_skills"],
            jd_extracted,
            resume_proc["normalized_text"]
        )
        overall_progress.progress(78, text="Gap analysis complete")
        time.sleep(0.3)

        # STAGE 6 — Multi-Agent System
        status_text.markdown(
            "**Stage 6/6 — 🤝 Running 4-agent AI system "
            "(this takes 1–3 minutes)…**"
        )
        crew_manager  = ResumifyCrewManager()
        agent_outputs = crew_manager.run_analysis(
            resume_text=resume_proc["normalized_text"],
            jd_text=jd_proc["full_text"],
            ats_result=ats_result,
            semantic_result=semantic_result,
            gap_analysis=gap_analysis,
            jd_extracted=jd_extracted
        )
        overall_progress.progress(100, text="✅ Analysis complete!")
        status_text.empty()
        time.sleep(0.5)
        overall_progress.empty()

        st.success("🎉 Analysis complete! Scroll down to see your results.")

        # ══════════════════════════════════════════════════════════════════════
        # ── RESULTS ──────────────────────────────────────────────────────────
        # ══════════════════════════════════════════════════════════════════════

        # ── Score Dashboard ───────────────────────────────────────────────────
        st.markdown("""
        <div class="section-header">
          <h2>📊 Score Dashboard</h2>
        </div>
        """, unsafe_allow_html=True)

        ats_score   = ats_result["total_score"]
        match_score = semantic_result["overall_score"]
        doc_sim     = doc_similarity

        c1, c2, c3, c4 = st.columns(4)

        for col, label, value, suffix, note in [
            (c1, "ATS Score",       ats_score,   "/100",  ats_result["grade"]),
            (c2, "Skill Match",     match_score, "%",     f"{semantic_result['matched_count']}/{semantic_result['total_jd_skills']} skills"),
            (c3, "Doc Similarity",  doc_sim,     "%",     "Resume ↔ JD"),
            (c4, "Missing Skills",  len(semantic_result["missing_skills"]), "", "to close the gap"),
        ]:
            color = score_color(float(value)) if label != "Missing Skills" else "#FF8800"
            with col:
                st.markdown(f"""
                <div class="score-card">
                  <p class="score-number" style="color:{color};">{value}{suffix}</p>
                  <p class="score-label">{label}</p>
                  <p style="color:#64748b;font-size:.78rem;margin:4px 0 0;">{note}</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── ATS Breakdown Bar Chart ───────────────────────────────────────────
        with st.expander("📈 ATS Score Breakdown", expanded=True):
            breakdown = ats_result["breakdown"]
            max_pts   = ATS_WEIGHTS = {
                "contact_info": 15, "section_headers": 20, "bullet_points": 15,
                "file_format": 10,  "length": 10,           "no_tables": 10,
                "keywords": 10,     "dates_format": 10
            }
            labels = {
                "contact_info": "Contact Info",     "section_headers": "Section Headers",
                "bullet_points": "Bullet Points",   "file_format": "File Format",
                "length": "Resume Length",           "no_tables": "No Tables",
                "keywords": "Keyword Density",       "dates_format": "Date Formatting"
            }
            for key, pts in breakdown.items():
                max_v = ATS_WEIGHTS.get(key, 10)
                pct   = (pts / max_v) * 100
                color = score_color(pct)
                st.markdown(f"""
                <div style="margin:8px 0;">
                  <div style="display:flex;justify-content:space-between;
                              font-size:.85rem;color:#94a3b8;margin-bottom:4px;">
                    <span>{labels.get(key, key)}</span>
                    <span style="color:{color};font-weight:700;">{pts}/{max_v}</span>
                  </div>
                  <div class="progress-bar-bg">
                    <div class="progress-bar-fill"
                         style="width:{pct}%;background:{color};"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            if ats_result["issues"]:
                st.markdown("**🔍 Issues Detected:**")
                for issue in ats_result["issues"]:
                    st.markdown(f"- {issue}")

        # ── Tabs for Results ──────────────────────────────────────────────────
        tabs = st.tabs([
            "🎯 Skill Match",
            "🔥 Skill Gaps",
            "🕵️ Resume Analysis",
            "📋 ATS Improvements",
            "🗺️ Learning Roadmap",
            "🌐 Resources"
        ])

        # ── Tab 1: Skill Match ─────────────────────────────────────────────
        with tabs[0]:
            st.markdown("""
            <div class="section-header">
              <h2>🎯 Semantic Skill Matching Results</h2>
            </div>
            """, unsafe_allow_html=True)

            job_title_display = jd_extracted.get("job_title", "Target Role")
            st.markdown(f"""
            <div class="info-box">
              🎯 <strong>Target Role:</strong> {job_title_display} &nbsp;|&nbsp;
              📊 Skills matched: <strong>{semantic_result['matched_count']}</strong> of
              <strong>{semantic_result['total_jd_skills']}</strong> JD skills found in your resume
            </div>
            """, unsafe_allow_html=True)

            fcol, mcol = st.columns(2)

            with fcol:
                st.markdown(f"#### ✅ Found in Resume ({len(semantic_result['found_skills'])})")
                if semantic_result["found_skills"]:
                    pills = "".join(
                        f'<span class="skill-pill-found">{s}</span>'
                        for s in semantic_result["found_skills"]
                    )
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.info("No matching skills detected.")

            with mcol:
                st.markdown(f"#### ❌ Missing from Resume ({len(semantic_result['missing_skills'])})")
                if semantic_result["missing_skills"]:
                    pills = "".join(
                        f'<span class="skill-pill-missing">{s}</span>'
                        for s in semantic_result["missing_skills"]
                    )
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.success("🎉 All detected skills are present in your resume!")

            # Show similarity scores for top missing skills
            if semantic_result["missing_skills"] and semantic_result["skill_scores"]:
                st.markdown("#### 🔢 Similarity Scores for Missing Skills")
                missing_scores = {
                    k: v for k, v in semantic_result["skill_scores"].items()
                    if k in semantic_result["missing_skills"]
                }
                sorted_scores = sorted(missing_scores.items(),
                                       key=lambda x: x[1], reverse=True)[:12]
                for skill, sim in sorted_scores:
                    pct   = sim * 100
                    color = score_color(pct)
                    st.markdown(f"""
                    <div style="margin:6px 0;">
                      <div style="display:flex;justify-content:space-between;
                                  font-size:.83rem;color:#94a3b8;margin-bottom:3px;">
                        <span>{skill}</span>
                        <span style="color:{color};font-weight:700;">{pct:.1f}%</span>
                      </div>
                      <div class="progress-bar-bg">
                        <div class="progress-bar-fill"
                             style="width:{pct}%;background:{color};"></div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

        # ── Tab 2: Skill Gaps ─────────────────────────────────────────────
        with tabs[1]:
            st.markdown("""
            <div class="section-header">
              <h2>🔥 Skill Gap Analysis & Priority Ranking</h2>
            </div>
            """, unsafe_allow_html=True)

            if gap_analysis.get("summary"):
                st.markdown(f"""
                <div class="info-box">📝 {gap_analysis['summary']}</div>
                """, unsafe_allow_html=True)

            g1, g2, g3 = st.columns(3)

            with g1:
                must = gap_analysis.get("must_have", [])
                st.markdown(f"""
                <div style="background:rgba(239,68,68,.1);border:1px solid #991b1b;
                            border-radius:14px;padding:18px;">
                  <div style="color:#fca5a5;font-weight:700;font-size:1rem;
                              margin-bottom:12px;">🔴 MUST HAVE ({len(must)})</div>
                  <div style="color:#6b7280;font-size:.78rem;margin-bottom:10px;">
                    Critical — rejection risk without these
                  </div>
                """, unsafe_allow_html=True)
                for s in must:
                    st.markdown(f'<span class="skill-pill-must">{s}</span>',
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with g2:
                good = gap_analysis.get("good_to_have", [])
                st.markdown(f"""
                <div style="background:rgba(251,191,36,.08);border:1px solid #92400e;
                            border-radius:14px;padding:18px;">
                  <div style="color:#fde68a;font-weight:700;font-size:1rem;
                              margin-bottom:12px;">🟡 GOOD TO HAVE ({len(good)})</div>
                  <div style="color:#6b7280;font-size:.78rem;margin-bottom:10px;">
                    Competitive advantage — learn after must-haves
                  </div>
                """, unsafe_allow_html=True)
                for s in good:
                    st.markdown(f'<span class="skill-pill-good">{s}</span>',
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with g3:
                bonus = gap_analysis.get("bonus", [])
                st.markdown(f"""
                <div style="background:rgba(56,189,248,.08);border:1px solid #0c4a6e;
                            border-radius:14px;padding:18px;">
                  <div style="color:#7dd3fc;font-weight:700;font-size:1rem;
                              margin-bottom:12px;">🔵 BONUS ({len(bonus)})</div>
                  <div style="color:#6b7280;font-size:.78rem;margin-bottom:10px;">
                    Differentiators — learn when ready
                  </div>
                """, unsafe_allow_html=True)
                for s in bonus:
                    st.markdown(f'<span class="skill-pill-bonus">{s}</span>',
                                unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # JD Metadata
            st.markdown("---")
            st.markdown("#### 📋 Job Description Insights")
            m1, m2, m3 = st.columns(3)
            m1.metric("Experience Required",
                      jd_extracted.get("experience_required", "N/A"))
            m2.metric("Education Required",
                      jd_extracted.get("education_required", "N/A"))
            m3.metric("Total JD Skills Found",
                      str(len(jd_skills)))

        # ── Tab 3: Resume Analysis (Agent Output) ─────────────────────────
        with tabs[2]:
            st.markdown("""
            <div class="section-header">
              <h2>🕵️ Resume Analyzer Agent Report</h2>
            </div>
            """, unsafe_allow_html=True)
            content = agent_outputs.get("resume_analysis", "")
            if content:
                st.markdown(f"""
                <div class="agent-card">
                  <div class="agent-title">
                    🤖 <span style="color:#a78bfa;">Resume Analyzer Agent</span>
                  </div>
                  {clean_markdown(content).replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Agent output not available.")

        # ── Tab 4: ATS Improvements (Agent Output) ─────────────────────────
        with tabs[3]:
            st.markdown("""
            <div class="section-header">
              <h2>📋 ATS Improvement Checklist</h2>
            </div>
            """, unsafe_allow_html=True)
            content = agent_outputs.get("ats_improvements", "")
            if content:
                st.markdown(f"""
                <div class="agent-card">
                  <div class="agent-title">
                    ⚡ <span style="color:#60a5fa;">ATS Optimization Agent</span>
                  </div>
                  {clean_markdown(content).replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Agent output not available.")

        # ── Tab 5: Learning Roadmap (Agent Output) ─────────────────────────
        with tabs[4]:
            st.markdown("""
            <div class="section-header">
              <h2>🗺️ Personalized Learning Roadmap</h2>
            </div>
            """, unsafe_allow_html=True)
            content = agent_outputs.get("learning_roadmap", "")
            if content:
                st.markdown(f"""
                <div class="agent-card">
                  <div class="agent-title">
                    🧭 <span style="color:#34d399;">Career Assistant Agent</span>
                  </div>
                  {clean_markdown(content).replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Agent output not available.")

        # ── Tab 6: Web Resources (Agent Output) ───────────────────────────
        with tabs[5]:
            st.markdown("""
            <div class="section-header">
              <h2>🌐 Learning Resources from the Web</h2>
            </div>
            """, unsafe_allow_html=True)
            content = agent_outputs.get("resources", "")
            if content:
                st.markdown(f"""
                <div class="agent-card">
                  <div class="agent-title">
                    🔍 <span style="color:#f59e0b;">Web Search Agent</span>
                  </div>
                  {clean_markdown(content).replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Agent output not available.")

        # ── Download Section ─────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("""
        <div class="section-header">
          <h2>💾 Export Your Analysis</h2>
        </div>
        """, unsafe_allow_html=True)

        report_text = f"""
RESUMIFY — YOUR JOB MATE | ANALYSIS REPORT
==========================================
Target Role     : {jd_extracted.get('job_title', 'N/A')}
ATS Score       : {ats_result['total_score']}/100  ({ats_result['grade']})
Skill Match     : {semantic_result['overall_score']}%
Doc Similarity  : {doc_similarity}%
Missing Skills  : {len(semantic_result['missing_skills'])}

──────────────────────────────────────────
ATS ISSUES
──────────────────────────────────────────
{chr(10).join(ats_result['issues'])}

──────────────────────────────────────────
FOUND SKILLS
──────────────────────────────────────────
{', '.join(semantic_result['found_skills'])}

──────────────────────────────────────────
MISSING SKILLS
──────────────────────────────────────────
Must Have    : {', '.join(gap_analysis.get('must_have', []))}
Good to Have : {', '.join(gap_analysis.get('good_to_have', []))}
Bonus        : {', '.join(gap_analysis.get('bonus', []))}

──────────────────────────────────────────
RESUME ANALYSIS
──────────────────────────────────────────
{agent_outputs.get('resume_analysis', 'N/A')}

──────────────────────────────────────────
ATS IMPROVEMENTS
──────────────────────────────────────────
{agent_outputs.get('ats_improvements', 'N/A')}

──────────────────────────────────────────
LEARNING ROADMAP
──────────────────────────────────────────
{agent_outputs.get('learning_roadmap', 'N/A')}

──────────────────────────────────────────
RESOURCES
──────────────────────────────────────────
{agent_outputs.get('resources', 'N/A')}
"""
        st.download_button(
            label="⬇️ Download Full Report (.txt)",
            data=report_text,
            file_name="resumify_analysis_report.txt",
            mime="text/plain",
            use_container_width=True
        )

    except Exception as e:
        overall_progress.empty()
        status_text.empty()
        st.error(f"❌ Analysis failed: {str(e)}")
        st.exception(e)

else:
    # ── Welcome State ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:50px 20px;color:#475569;">
      <div style="font-size:4rem;margin-bottom:16px;">📂</div>
      <div style="font-size:1.3rem;font-weight:600;color:#64748b;">
        Upload your resume and paste a job description above to get started
      </div>
      <div style="font-size:.95rem;margin-top:10px;color:#374151;">
        Resumify will analyze your resume, score it for ATS compatibility,
        match it against the job description using AI, and give you a
        personalized roadmap to land that role.
      </div>
    </div>

    <div style="display:flex;justify-content:center;gap:24px;
                flex-wrap:wrap;margin-top:32px;">
      <div style="background:#111827;border:1px solid #1e293b;border-radius:14px;
                  padding:20px 28px;text-align:center;min-width:160px;">
        <div style="font-size:2rem;">📊</div>
        <div style="font-weight:700;color:#a78bfa;margin-top:8px;">ATS Score</div>
        <div style="font-size:.8rem;color:#6b7280;margin-top:4px;">Resume compatibility check</div>
      </div>
      <div style="background:#111827;border:1px solid #1e293b;border-radius:14px;
                  padding:20px 28px;text-align:center;min-width:160px;">
        <div style="font-size:2rem;">🔍</div>
        <div style="font-weight:700;color:#60a5fa;margin-top:8px;">Skill Match</div>
        <div style="font-size:.8rem;color:#6b7280;margin-top:4px;">AI-powered JD analysis</div>
      </div>
      <div style="background:#111827;border:1px solid #1e293b;border-radius:14px;
                  padding:20px 28px;text-align:center;min-width:160px;">
        <div style="font-size:2rem;">🗺️</div>
        <div style="font-weight:700;color:#34d399;margin-top:8px;">Roadmap</div>
        <div style="font-size:.8rem;color:#6b7280;margin-top:4px;">Personalized learning plan</div>
      </div>
      <div style="background:#111827;border:1px solid #1e293b;border-radius:14px;
                  padding:20px 28px;text-align:center;min-width:160px;">
        <div style="font-size:2rem;">🌐</div>
        <div style="font-weight:700;color:#f59e0b;margin-top:8px;">Resources</div>
        <div style="font-size:.8rem;color:#6b7280;margin-top:4px;">Curated learning links</div>
      </div>
    </div>
    """, unsafe_allow_html=True)