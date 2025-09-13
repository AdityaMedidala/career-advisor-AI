from urllib.parse import quote_plus

def google_jobs(role: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(role + ' remote jobs')}"

def indeed(role: str) -> str:
    return f"https://www.indeed.com/jobs?q={quote_plus(role)}&sc=0kf%3Aattr%28DSQF7%29%3B"

def linkedin(role: str) -> str:
    return f"https://www.linkedin.com/jobs/search/?keywords={quote_plus(role)}"

def job_links(role: str) -> dict:
    return {"Google Jobs": google_jobs(role), "Indeed": indeed(role), "LinkedIn": linkedin(role)}

def refined_google_jobs(role: str, matching_skills: list[str]) -> str:
    """Creates a targeted job search query including the user's top skills."""
    skills_query = " AND ".join(f'"{s}"' for s in matching_skills[:3])
    full_query = f'{role} jobs with {skills_query} remote'
    # The &ibp=htl;jobs part takes the user directly to the Google Jobs interface
    return f"https://www.google.com/search?q={quote_plus(full_query)}&ibp=htl;jobs"