import json, pathlib
from typing import List, Dict

def load_occupations() -> List[Dict]:
    return json.loads(pathlib.Path("data/occupations.json").read_text(encoding="utf-8"))

def rank_roles(user_skills: list[str], occupations: list[dict], top_k: int = 5):
    user_set = set(user_skills)
    results = []
    for o in occupations:
        req = list(dict.fromkeys(o.get("skills_required", [])))  # unique, keep order
        overlap = len(user_set.intersection(req)) / max(1, len(req))
        gaps = [s for s in req if s not in user_set]
        results.append({**o, "score": round(overlap, 3), "gaps": gaps})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def skill_gaps(target_role: dict, user_skills: list[str]):
    return [s for s in target_role.get("skills_required", []) if s not in set(user_skills)]
