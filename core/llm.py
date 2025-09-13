import os, json, re
import google.generativeai as genai

# Configure once at import
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY in environment (.env)")
genai.configure(api_key=API_KEY)

MODEL_NAME = os.getenv("LLM_MODEL", "gemini-1.5-flash")

def _make_model():
    # You can tweak safety settings here if needed
    return genai.GenerativeModel(MODEL_NAME)

def _call_gemini(prompt: str) -> str:
    model = _make_model()
    resp = model.generate_content(prompt)
    # The SDK returns text in resp.text
    return (resp.text or "").strip()

def extract_skills(text: str):
    """
    Ask Gemini to return JSON array of normalized skills.
    """
    prompt = f"""
You are a skill extraction engine.
From the following resume/profile text, output a JSON array (no prose) of 10-25 normalized skills.
Normalize common variants (e.g., "MS Excel" => "Excel", "PostgreSQL" => "SQL").
Return ONLY valid JSON.

TEXT:
{text}
"""
    raw = _call_gemini(prompt)
    # Strip code fences if model returns ```json ... ```
    raw = re.sub(r"^```json|```$", "", raw, flags=re.IGNORECASE | re.MULTILINE).strip()
    try:
        data = json.loads(raw)
        # ensure it's a list of strings
        return [str(x).strip() for x in data if isinstance(x, (str, int, float))]
    except Exception:
        # fallback: try to split lines
        return [s.strip("- *•\t ").strip() for s in raw.splitlines() if s.strip()][:15]

def generate_roadmap(profile: dict, target_role: str, gaps: list[str]) -> str:
    """
    Produce a concise, weekly roadmap.
    """
    skills = profile.get("skills", [])
    prompt = f"""
You are a career and education advisor. Create a **6-week, practical roadmap** for becoming a {target_role}.
User's current skills: {skills}
Skill gaps to address: {gaps}

Constraints:
- Keep it under ~300 words.
- Weekly phases (Week 1..6) with 3-5 bullet tasks each.
- Prioritize free/low-cost resources (MOOCs, YouTube, docs).
- Include one small portfolio project idea and suggested job-search activities.
- Return clean Markdown (no front matter).
"""
    return _call_gemini(prompt)
