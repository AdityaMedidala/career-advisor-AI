from urllib.parse import quote_plus

def google_course_search(term: str) -> str:
    return f"https://www.google.com/search?q={quote_plus(term + ' course beginner')}"

def coursera_search(term: str) -> str:
    return f"https://www.google.com/search?q={quote_plus('site:coursera.org ' + term)}"

def edx_search(term: str) -> str:
    return f"https://www.google.com/search?q={quote_plus('site:edx.org ' + term)}"

def links_for_gap(gap: str) -> dict:
    return {
        "Google": google_course_search(gap),
        "Coursera": coursera_search(gap),
        "edX": edx_search(gap),
        "YouTube": f"https://www.youtube.com/results?search_query={quote_plus(gap+' tutorial')}"
    }
