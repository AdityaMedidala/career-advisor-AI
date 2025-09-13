import json, pathlib, re
from rapidfuzz import fuzz

_TAX = json.loads(pathlib.Path("data/skills_taxonomy.json").read_text(encoding="utf-8"))

def _alias(s: str) -> str:
    k = s.lower().strip()
    return _TAX.get(k, s)

def normalize_skills(skills: list[str]) -> list[str]:
    # Basic clean + alias map + fuzzy dedupe
    cleaned = []
    for s in skills:
        s = re.sub(r"[^a-zA-Z0-9+#.\s/-]", "", str(s)).strip()
        if not s: 
            continue
        s = _alias(s)
        cleaned.append(s)

    out = []
    for s in cleaned:
        if not any(fuzz.ratio(s, t) > 90 for t in out):
            out.append(s)
    # de-dupe & sort
    return sorted(set(out), key=str.lower)
