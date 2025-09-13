import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import time

# --- CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=API_KEY)
MODEL = genai.GenerativeModel("gemini-1.5-flash")

# --- LIST OF ROLES TO GENERATE DATA FOR ---
TARGET_ROLES = [
    "Data Scientist", "DevOps Engineer", "UI/UX Designer", "Digital Marketer",
    "IT Project Manager", "Business Analyst", "Mobile App Developer",
    "Technical Writer", "Network Engineer", "QA Engineer", "Machine Learning Engineer",
    "Frontend Developer", "Backend Developer", "Full Stack Developer", "Database Administrator"
]

# --- PROMPT TO GENERATE DATA IN THE CORRECT FORMAT ---
PROMPT_TEMPLATE = """
You are a hiring and skills expert. For the role of "{role_name}", generate a JSON object.

The JSON object must have two keys:
1. "occupation": The string "{role_name}".
2. "skills_required": A JSON array of 7-10 skill objects.

Each skill object in the array must have two keys:
1. "skill": The name of the skill (e.g., "Python").
2. "weight": An integer from 1 (secondary importance) to 5 (critically important).

Return ONLY the raw JSON object, with no markdown fences or explanations.
"""

def generate_role_data(role_name):
    """Calls Gemini to generate the structured JSON for a single role."""
    print(f"Generating data for: {role_name}...")
    prompt = PROMPT_TEMPLATE.format(role_name=role_name)
    try:
        response = MODEL.generate_content(prompt)
        cleaned_json = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_json)
    except Exception as e:
        print(f"  -> Failed to generate or parse data for {role_name}: {e}")
        return None

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Load existing starter data to append to
    with open("data/occupations.json", "r", encoding="utf-8") as f:
        all_roles_data = json.load(f)
    print(f"Loaded {len(all_roles_data)} existing roles.")

    for role in TARGET_ROLES:
        role_data = generate_role_data(role)
        if role_data:
            all_roles_data.append(role_data)
        time.sleep(1) # To avoid hitting API rate limits

    output_filename = "data/occupations_expanded.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(all_roles_data, f, indent=2)

    print(f"\n✅ Successfully generated data for {len(TARGET_ROLES)} new roles.")
    print(f"Total roles in new file: {len(all_roles_data)}")
    print(f"New dataset saved to {output_filename}")
    print("-> Next, update core/scoring.py to use this new file!")