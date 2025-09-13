import os, json, re
import google.generativeai as genai

# Configure once at import
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY in environment (.env)")
genai.configure(api_key=API_KEY)

MODEL_NAME = os.getenv("LLM_MODEL", "gemini-1.5-flash")
MODEL = genai.GenerativeModel(MODEL_NAME)

def _call_gemini(prompt: str) -> str:
    resp = MODEL.generate_content(prompt)
    return (resp.text or "").strip()

def extract_skills(text: str):
    """Ask Gemini to return JSON array of normalized skills."""
    prompt = f"""
You are a skill extraction engine. From the following resume/profile text, output a JSON array (no prose) of 10-25 normalized skills. Normalize common variants (e.g., "MS Excel" => "Excel", "PostgreSQL" => "SQL"). Return ONLY valid JSON.
TEXT:
{text}
"""
    raw = _call_gemini(prompt)
    raw = re.sub(r"^```json|```$", "", raw, flags=re.IGNORECASE | re.MULTILINE).strip()
    try:
        data = json.loads(raw)
        return [str(x).strip() for x in data if isinstance(x, (str, int, float))]
    except Exception:
        return [s.strip("- *•\t ").strip() for s in raw.splitlines() if s.strip()][:15]

def generate_roadmap(profile: dict, target_role: str, gaps: list[str], hours: int, style: str) -> str:
    """Produce a concise, weekly roadmap, personalized to user preferences."""
    skills = profile.get("skills", [])
    prompt = f"""
You are a career advisor. Create a **6-week, practical roadmap** for becoming a {target_role}.
USER PROFILE:
- Current skills: {skills}
- Skill gaps to address: {gaps}
- Can commit {hours} hours per week.
- Prefers a learning style focused on: {style}.
CONSTRAINTS:
- Keep it under ~300 words.
- Structure into weekly phases (Week 1..6) with 3-5 bulleted tasks each.
- Prioritize free/low-cost resources (MOOCs, YouTube, docs).
- Include one small portfolio project idea and job-search activities.
- Return clean Markdown.
"""
    return _call_gemini(prompt)

def suggest_skills_for_role(role: str) -> list[str]:
    """Uses Gemini to find current, in-demand skills for a given job role."""
    prompt = f"""
Act as a job market analyst. For the role of "{role}", list the top 10 most in-demand technical skills and software tools I should know in 2025. Return a clean JSON array of strings. Do not include soft skills. Return ONLY the raw JSON array.
"""
    raw = _call_gemini(prompt)
    raw = re.sub(r"^```json|```$", "", raw, flags=re.IGNORECASE | re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except Exception:
        return [s.strip("- *•\t ").strip() for s in raw.splitlines() if s.strip()]

def get_strategic_insights(user_skills: list[str]) -> str:
    """Analyzes a user's skills to provide proactive synergy and career adjacency insights."""
    prompt = f"""
Act as a world-class career strategist. A user has the following skills: {user_skills}.
Perform two distinct analyses and return the result as a single Markdown response:
1.  **Skill Synergy Insights:** Identify 2-3 skills that are highly complementary to their existing skillset and explain why in one sentence. Frame these as easy wins or natural next steps.
2.  **Adjacent Career Paths:** Based on their unique skill combination, suggest 1-2 non-obvious "adjacent" or "transitional" career paths they might not have considered. Briefly explain the skill overlap.
"""
    return _call_gemini(prompt)

def generate_learning_module(skill: str) -> str:
    """Generates a 'Day 1' micro-learning module for a specific skill."""
    prompt = f"""
Act as an expert technical instructor. Create a "First Steps" micro-learning module for the skill: **{skill}**.
The module should be concise, beginner-friendly, and returned as a single Markdown block.
The module must contain these four sections:
1.  **## 🎯 What is {skill}?** A simple, one-paragraph explanation using an analogy.
2.  **## 🔑 Key Concepts** A bulleted list of the 3 most important foundational terms or ideas.
3.  **## 🚀 Your First Practical Step** A small, hands-on "Hello, World!" style code snippet or a simple, actionable instruction.
4.  **## ✅ Knowledge Check** A single multiple-choice question with three options (A, B, C) to test the core concept. Provide the correct answer at the end.
"""
    return _call_gemini(prompt)

def run_career_discovery_agent(user_skills: list[str]) -> str:
    """Acts as an autonomous agent to discover and analyze career paths."""
    prompt = f"""
Act as an autonomous AI career discovery agent. Your input is a list of a user's skills. Your goal is to identify and analyze the top 3 most promising career paths for them.
Execute the following four steps in order and return the final report as a single, clean Markdown response. Do not output your internal thoughts for each step, only the final report.
**Step 1: Foundational Skill Analysis** Review the user's skills: {user_skills}. Identify the core competency.
**Step 2: Career Path Hypothesis** Based on the core competency, brainstorm a list of 5-7 potential job titles.
**Step 3: Internal Gap Analysis & Scoring** For each hypothesized job title, perform a silent, internal gap analysis. Determine the key skills required for that role and calculate a "Fit Score" from 1 to 100.
**Step 4: Synthesize Final Report** Present a final report in Markdown. The report must include: a title, the user's Core Competency, a ranked list of the Top 3 Career Paths with their Fit Score and a Brief Rationale.
"""
    return _call_gemini(prompt)

def generate_resume_bullets(role: str, user_skills: list[str], gaps: list[str]) -> str:
    """Generates resume bullet points to bridge skill gaps."""
    prompt = f"""
Act as a professional resume writer. A user wants to apply for a **{role}** role.
- Their current skills are: {user_skills}
- Their identified skill gaps for the role are: {gaps}

Generate 2-3 powerful, concise resume bullet points. Each bullet point should creatively frame their EXISTING skills to align with the needs of the target role, helping to minimize the perceived gaps. The tone should be professional and action-oriented. Return only the bullet points in Markdown format.
"""
    return _call_gemini(prompt)

def generate_interview_questions(role: str, user_skills: list[str]) -> str:
    """Generates mock interview questions for a role."""
    prompt = f"""
Act as a hiring manager for a **{role}** position.
- The candidate's skills are: {user_skills}

Generate a mix of 4 interview questions for this candidate:
- 2 behavioral questions.
- 2 technical questions relevant to their skills and the role.

For each question, provide a brief, one-sentence hint on what a great answer should cover.
Format the output as clean Markdown.
"""
    return _call_gemini(prompt)