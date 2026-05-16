# 🚀 Resumify — Your Job Mate!

> **AI-powered resume analysis, ATS scoring, skill gap detection, and personalized career roadmaps.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-6C3EFF?style=for-the-badge)
![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM-00C2FF?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 📌 What Is Resumify?

**Resumify** is a full-stack AI career assistant that takes your resume and a job description and gives you everything you need to land the job — from ATS compatibility scores to a week-by-week learning roadmap.

Unlike other resume tools, Resumify **never uses a predefined list of skills**. All skills and tools are dynamically extracted from the job description using AI, then semantically matched against your resume using vector embeddings.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **Resume Parsing** | Supports PDF and DOCX. Extracts and normalizes text section by section (Summary, Education, Experience, Skills) |
| 📋 **JD Analysis** | Parses the job description and extracts required skills, tools, responsibilities, and experience levels using AI |
| 📊 **ATS Score** | Scores your resume out of 100 across 8 criteria — contact info, section headers, bullet points, formatting, length, dates, and keyword density |
| 🔍 **Semantic Skill Matching** | Uses `sentence-transformers` + cosine similarity to match JD-extracted skills against your resume — no hardcoded lists |
| 🔥 **Gap Analysis** | Classifies missing skills into **Must Have**, **Good to Have**, and **Bonus** using LLM reasoning |
| 🕵️ **Resume Analyzer Agent** | Finds strengths, weaknesses, and gives specific improvement suggestions |
| ⚡ **ATS Agent** | Provides a prioritized checklist: Critical Fixes, Keyword Optimization, Formatting Fixes, and Quick Wins |
| 🗺️ **Career Assistant Agent** | Builds a personalized phase-by-phase learning roadmap |
| 🌐 **Web Search Agent** | Searches DuckDuckGo for real courses, tutorials, YouTube playlists, and articles for each missing skill |
| 💾 **Export** | Download your full analysis as a `.txt` report |

---

## 🏗️ Architecture

```
resumify/
├── app.py                    ← Streamlit frontend (main entry point)
├── .env                      ← API keys and model configuration
├── requirements.txt
│
├── config/
│   └── settings.py           ← API config, ATS weights, thresholds
│
├── core/
│   ├── parser.py             ← PDF & DOCX parser
│   ├── preprocessor.py       ← Text cleaning, normalization, section extraction
│   ├── ats_checker.py        ← ATS scoring engine (8 criteria, 100-point scale)
│   ├── skill_extractor.py    ← LLM-based skill extraction from JD (no predefined lists)
│   ├── semantic_matcher.py   ← Sentence-transformer + cosine similarity matching
│   └── gap_analyzer.py       ← LLM-based skill gap prioritization
│
├── agents/
│   ├── llm_config.py         ← OpenRouter LLM configuration for CrewAI
│   ├── resume_analyzer_agent.py
│   ├── ats_agent.py
│   ├── career_assistant_agent.py
│   ├── web_search_agent.py   ← DuckDuckGo search tool + agent
│   └── crew_manager.py       ← Orchestrates the 4-agent CrewAI pipeline
│
└── utils/
    └── helpers.py            ← Score colors, badge formatting, utilities
```

---

## 🤖 Multi-Agent System

Resumify uses **CrewAI** to orchestrate 4 specialized AI agents that run sequentially:

```
┌─────────────────────────────────────────────────────────┐
│                    CrewAI Pipeline                      │
│                                                         │
│  1. Resume Analyzer Agent                               │
│     → Strengths, Weaknesses, Improvement Suggestions   │
│                        ↓                               │
│  2. ATS Optimization Agent                              │
│     → Critical Fixes, Keywords, Formatting, Quick Wins │
│                        ↓                               │
│  3. Career Assistant Agent                              │
│     → Phase 1-3 Learning Roadmap, Daily Practice Plan  │
│                        ↓                               │
│  4. Web Search Agent (DuckDuckGo)                       │
│     → Courses, Tutorials, Videos, Articles per skill   │
└─────────────────────────────────────────────────────────┘
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit with custom CSS (dark theme, gradient UI) |
| **LLM API** | OpenRouter (supports 300+ models including free tiers) |
| **Multi-Agent** | CrewAI (sequential process) |
| **Semantic Matching** | `sentence-transformers` — `all-MiniLM-L6-v2` model |
| **Similarity** | Cosine similarity via `scikit-learn` |
| **PDF Parsing** | `pdfplumber` |
| **DOCX Parsing** | `python-docx` |
| **Web Search** | `duckduckgo-search` (no API key required) |
| **HTTP Client** | `requests` (direct OpenRouter calls for reliability) |

---

## 🛠️ Setup & Installation (Windows)

### Prerequisites

- Python 3.10 or 3.11 — [python.org](https://python.org/downloads)
- VS Code — [code.visualstudio.com](https://code.visualstudio.com)
- OpenRouter API Key — [openrouter.ai](https://openrouter.ai) *(free tier available)*

### Step 1 — Clone or Download the Project

```bash
cd resumify
```

### Step 2 — Create a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

> ⏳ First install takes 5–10 minutes due to PyTorch and sentence-transformers.

### Step 4 — Configure API Keys

Create a `.env` file in the root directory:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
MODEL_NAME=openrouter/meta-llama/llama-3.3-70b-instruct:free
```

### Step 5 — Run the App

```bash
streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`.

---

## 🔑 Choosing an OpenRouter Model

Visit [openrouter.ai/models](https://openrouter.ai/models) and filter by **Free** to see available options.

| Model | Cost | Quality | Recommended For |
|---|---|---|---|
| `meta-llama/llama-3.3-70b-instruct:free` | Free | ⭐⭐⭐⭐ | Best free option — recommended |
| `nvidia/nemotron-3-super-120b-a12b:free` | Free | ⭐⭐⭐⭐⭐ | High quality, may be slower |
| `openrouter/free` | Free | ⭐⭐⭐ | Auto-selects — most reliable uptime |
| `google/gemini-flash-1.5` | Paid (cheap) | ⭐⭐⭐⭐⭐ | Best quality, ~$0.001 per analysis |

> **Note:** Free model availability changes frequently. If you see a `404` error, switch to `openrouter/openrouter/free` which auto-routes to whatever is available.

---

## 📊 ATS Scoring Criteria

The ATS score is calculated across 8 weighted criteria:

| Criteria | Weight | What It Checks |
|---|---|---|
| Contact Info | 15 pts | Email, phone number, LinkedIn URL |
| Section Headers | 20 pts | Experience, Education, Skills sections present |
| Bullet Points | 15 pts | Sufficient use of bullet points |
| File Format | 10 pts | PDF or DOCX format |
| Resume Length | 10 pts | 200–1200 words (1–2 pages) |
| No Tables | 10 pts | Absence of table/column layouts |
| Keyword Density | 10 pts | Skills/Technologies section present |
| Date Formatting | 10 pts | Consistent date formats |

---

## 🔍 How Skill Matching Works

**Resumify does not use any predefined skill lists.** Here's the pipeline:

```
Job Description Text
        ↓
  LLM Skill Extraction (OpenRouter)
  → must_have_skills, tools_and_technologies,
    good_to_have_skills, soft_skills, domain_knowledge
        ↓
  All skills flattened into a single list
        ↓
  Sentence-Transformer Encoding (all-MiniLM-L6-v2)
        ↓
  Resume chunked into overlapping 150-word windows
        ↓
  Cosine Similarity per skill vs. all resume chunks
        ↓
  Threshold check (default: 0.42)
  → ✅ Found  or  ❌ Missing
        ↓
  Gap Analyzer (LLM) classifies missing skills into:
  Must Have | Good to Have | Bonus
```

---

## 📤 Output Tabs

After analysis, Resumify shows results across 6 tabs:

1. **🎯 Skill Match** — Visual breakdown of found vs. missing skills with similarity scores
2. **🔥 Skill Gaps** — Must Have / Good to Have / Bonus priority cards + JD insights
3. **🕵️ Resume Analysis** — Agent report: Strengths, Weaknesses, Suggestions
4. **📋 ATS Improvements** — Checklist: Critical Fixes, Keywords, Formatting, Quick Wins
5. **🗺️ Learning Roadmap** — Phase 1-3 roadmap with daily practice plan
6. **🌐 Resources** — Real web links to courses, tutorials, videos, and articles

---

## 🐛 Troubleshooting

| Error | Fix |
|---|---|
| `404 No endpoints found` | The model was deprecated. Change `MODEL_NAME` in `.env` to `openrouter/openrouter/free` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` with the venv activated |
| Skills showing as 0 | Check your OpenRouter API key is valid; add credits if on free tier rate limit |
| Agents cut off mid-response | Switch to a higher-quality model like `google/gemini-flash-1.5` |
| `torch` install fails | Run: `pip install torch --index-url https://download.pytorch.org/whl/cpu` |
| `venv\Scripts\activate` fails | Run VS Code as Administrator or use `Set-ExecutionPolicy RemoteSigned` in PowerShell |

---

## 📦 requirements.txt

```
streamlit>=1.32.0
crewai>=0.80.0
crewai-tools>=0.20.0
pdfplumber>=0.11.0
python-docx>=1.1.0
sentence-transformers>=3.0.0
scikit-learn>=1.5.0
python-dotenv>=1.0.0
openai>=1.30.0
torch>=2.2.0
numpy>=1.26.0
pandas>=2.2.0
requests>=2.31.0
duckduckgo-search>=6.1.0
```

---

## 📁 .env Template

```env
# Required
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Model — change this if you get a 404 error
MODEL_NAME=openrouter/meta-llama/llama-3.3-70b-instruct:free
```

---

## 🚀 Quick Start (After Setup)

```bash
# 1. Activate virtual environment
venv\Scripts\activate

# 2. Run the app
streamlit run app.py

# 3. Open browser at http://localhost:8501
# 4. Upload your resume (PDF or DOCX)
# 5. Paste the job description
# 6. Click "Analyze My Resume"
# 7. Wait 1-3 minutes for AI analysis
# 8. View results across 6 tabs
# 9. Download full report
```

---

## 📄 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

## 🙏 Built With

- [Streamlit](https://streamlit.io) — Frontend UI
- [CrewAI](https://crewai.com) — Multi-agent orchestration
- [OpenRouter](https://openrouter.ai) — LLM API gateway
- [sentence-transformers](https://sbert.net) — Semantic embeddings
- [pdfplumber](https://github.com/jsvine/pdfplumber) — PDF parsing
- [python-docx](https://python-docx.readthedocs.io) — DOCX parsing
- [duckduckgo-search](https://github.com/deedy5/duckduckgo_search) — Web resource search

---

<div align="center">
  <strong>🚀 Resumify — Your Job Mate!</strong><br>
  Built with ❤️ using CrewAI · Streamlit · OpenRouter · sentence-transformers
</div>