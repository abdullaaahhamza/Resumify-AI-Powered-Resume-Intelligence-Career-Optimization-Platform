import json
from crewai import Task, Crew, Process
from agents.resume_analyzer_agent  import create_resume_analyzer_agent
from agents.ats_agent              import create_ats_agent
from agents.career_assistant_agent import create_career_assistant_agent
from agents.web_search_agent       import create_web_search_agent


class ResumifyCrewManager:
    """Orchestrates the 4-agent CrewAI multi-agent system."""

    def __init__(self):
        self.resume_agent  = create_resume_analyzer_agent()
        self.ats_agent     = create_ats_agent()
        self.career_agent  = create_career_assistant_agent()
        self.search_agent  = create_web_search_agent()

    def run_analysis(
        self,
        resume_text:     str,
        jd_text:         str,
        ats_result:      dict,
        semantic_result: dict,
        gap_analysis:    dict,
        jd_extracted:    dict
    ) -> dict:

        job_title   = jd_extracted.get("job_title", "target role")
        found       = semantic_result.get("found_skills",  [])
        must_have   = gap_analysis.get("must_have",    [])
        good_have   = gap_analysis.get("good_to_have", [])
        bonus       = gap_analysis.get("bonus",        [])
        missing_all = must_have + good_have + bonus
        ats_score   = ats_result.get("total_score", 0)
        ats_issues  = ats_result.get("issues",       [])
        match_score = semantic_result.get("overall_score", 0)

        # Truncate resume text to avoid context overflow
        resume_short = resume_text[:2000]

        # ── Task 1: Resume Analysis ──────────────────────────────────────────
        task_resume = Task(
            description=f"""Analyze this resume for a {job_title} position.

RESUME (first 2000 chars):
{resume_short}

MATCHED SKILLS (in resume): {json.dumps(found[:12])}
MISSING SKILLS: {json.dumps(missing_all[:12])}
MATCH SCORE: {match_score}%

Write a structured analysis with EXACTLY these 3 sections. Be concise and complete each section fully:

## STRENGTHS
- [3 specific strengths found in this resume]

## WEAKNESSES  
- [3 specific weaknesses or gaps]

## IMPROVEMENT SUGGESTIONS
- [5 specific, actionable things to add or change in this resume]

Keep total response under 400 words. Be direct and specific.""",
            expected_output=(
                "A structured report with three sections — Strengths, Weaknesses, "
                "and Improvement Suggestions — each with 3-5 bullet points. "
                "Total length: under 400 words."
            ),
            agent=self.resume_agent
        )

        # ── Task 2: ATS Improvements ─────────────────────────────────────────
        task_ats = Task(
            description=f"""The resume scored {ats_score}/100 on ATS compatibility for {job_title}.

ATS ISSUES FOUND:
{chr(10).join(ats_issues) if ats_issues else "No major issues detected."}

TOP JD KEYWORDS TO ADD: {json.dumps(jd_extracted.get("must_have_skills", [])[:8])}

Write EXACTLY these 4 sections. Complete ALL sections fully:

## CRITICAL FIXES
- [2-3 urgent formatting or content issues to fix immediately]

## KEYWORD OPTIMIZATION
- [3 specific keywords from the JD to add and WHERE to add them in the resume]

## FORMATTING FIXES
- [2-3 formatting changes for better ATS parsing]

## QUICK WINS
- [2-3 easy changes that immediately boost ATS score]

Keep total response under 350 words. Be specific and actionable.""",
            expected_output=(
                "Four clearly labeled sections: Critical Fixes, Keyword Optimization, "
                "Formatting Fixes, and Quick Wins. Each section has 2-3 bullet points. "
                "Total length: under 350 words."
            ),
            agent=self.ats_agent
        )

        # ── Task 3: Learning Roadmap ─────────────────────────────────────────
        task_career = Task(
            description=f"""Create a learning roadmap for someone targeting: {job_title}

SKILLS THEY HAVE: {json.dumps(found[:10])}

SKILLS TO LEARN:
- Must Have (urgent): {json.dumps(must_have[:6])}
- Good to Have: {json.dumps(good_have[:5])}
- Bonus: {json.dumps(bonus[:4])}

Write EXACTLY this structure. Complete ALL phases fully:

## PHASE 1 — WEEKS 1-4 (Must Have Skills)
- Skill: [skill name] | Time: [X weeks] | Focus: [what exactly to learn]
[cover each must-have skill]

## PHASE 2 — WEEKS 5-8 (Good to Have)
- Skill: [skill name] | Time: [X weeks] | Focus: [what exactly to learn]
[cover each good-to-have skill]

## PHASE 3 — WEEKS 9-12 (Bonus Skills)
- Skill: [skill name] | Time: [X weeks] | Focus: [what exactly to learn]

## DAILY PRACTICE PLAN
- [3 specific daily habits to build these skills]

## WHEN YOU'RE READY TO APPLY
- [2 milestone checkpoints that signal job-readiness]

Keep total response under 450 words.""",
            expected_output=(
                "A 3-phase learning roadmap covering all missing skills with "
                "timeline, focus areas, daily practice plan, and readiness checkpoints. "
                "Under 450 words total."
            ),
            agent=self.career_agent
        )

        # ── Task 4: Web Resources ────────────────────────────────────────────
        # Only search for top 4 must-have skills to stay within limits
        top_skills = (must_have + good_have)[:4]
        skills_str = ", ".join(top_skills) if top_skills else "general programming"

        task_search = Task(
            description=f"""Find learning resources for these skills needed for {job_title}:
{json.dumps(top_skills)}

For EACH skill, search and list resources in this exact format:

## [SKILL NAME]
- Course: [title and platform, e.g. "Python Bootcamp - Udemy"]
- Free Resource: [title and URL]
- YouTube: [channel or playlist name]
- Article: [title and URL or publication name]

Search for each skill one at a time using queries like:
- "learn {top_skills[0] if top_skills else 'Python'} tutorial for beginners 2024"
- "best {top_skills[0] if top_skills else 'Python'} course free"

Complete ALL {len(top_skills)} skills. Keep total response under 400 words.""",
            expected_output=(
                f"Learning resources for {len(top_skills)} skills, "
                "each with a course, free resource, YouTube link, and article. "
                "Under 400 words total."
            ),
            agent=self.search_agent
        )

        # ── Run Crew ─────────────────────────────────────────────────────────
        crew = Crew(
            agents=[
                self.resume_agent,
                self.ats_agent,
                self.career_agent,
                self.search_agent
            ],
            tasks=[task_resume, task_ats, task_career, task_search],
            process=Process.sequential,
            verbose=True
        )

        crew.kickoff()

        # ── Extract outputs safely ────────────────────────────────────────────
        def safe_output(task) -> str:
            try:
                out = task.output
                if out is None:
                    return ""
                if hasattr(out, "raw"):
                    return str(out.raw).strip()
                if hasattr(out, "result"):
                    return str(out.result).strip()
                return str(out).strip()
            except Exception:
                return ""

        return {
            "resume_analysis":  safe_output(task_resume),
            "ats_improvements": safe_output(task_ats),
            "learning_roadmap": safe_output(task_career),
            "resources":        safe_output(task_search)
        }