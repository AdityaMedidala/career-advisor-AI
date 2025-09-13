from urllib.parse import quote_plus

def google_jobs(role: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(role + ' remote jobs')}"

def indeed(role: str) -> str:
    return f"https://www.indeed.com/jobs?q={quote_plus(role)}&sc=0kf%3Aattr%28DSQF7%29%3B"

def linkedin(role: str) -> str:
    return f"https://www.linkedin.com/jobs/search/?keywords={quote_plus(role)}"

def job_links(role: str) -> dict:
    return {"Google Jobs": google_jobs(role), "Indeed": indeed(role), "LinkedIn": linkedin(role)}
