import json, pathlib
from typing import List, Dict
import streamlit as st

@st.cache_data
def load_occupations() -> List[Dict]:
    """Loads and caches the occupations data from the JSON file."""
    # Point to the new, larger, AI-generated dataset.
    return json.loads(pathlib.Path("data/occupations_expanded.json").read_text(encoding="utf-8"))

def rank_roles(user_skills: list[str], occupations: list[dict], top_k: int = 5):
    """Ranks roles based on a weighted score of matching skills."""
    user_set = set(user_skills)
    results = []
    for o in occupations:
        req_skills_with_weights = o.get("skills_required", [])
        total_possible_score = sum(s['weight'] for s in req_skills_with_weights)
        user_score = sum(s['weight'] for s in req_skills_with_weights if s['skill'] in user_set)
        normalized_score = user_score / max(1, total_possible_score)
        req_skills_list = [s['skill'] for s in req_skills_with_weights]
        gaps = [s for s in req_skills_list if s not in user_set]
        results.append({**o, "score": round(normalized_score, 3), "gaps": gaps})
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def skill_gaps(target_role: dict, user_skills: list[str]):
    req_skills = [s['skill'] for s in target_role.get("skills_required", [])]
    return [s for s in req_skills if s not in set(user_skills)]