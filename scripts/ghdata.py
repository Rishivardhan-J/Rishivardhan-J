"""Small shared GitHub helpers for the CI generators (stdlib only)."""
import json, os, urllib.request

USER = os.environ.get("PROFILE_USER", "Rishivardhan-J")
# Flutter platform runners and web build output: GitHub counts them as languages, but they aren't app code
SCAFFOLD = {"C", "C++", "CMake", "Objective-C", "Swift", "Kotlin", "Shell", "HTML", "Ruby"}


def rest(path):
    """GET https://api.github.com/<path> with the CI token and return the parsed JSON."""
    req = urllib.request.Request("https://api.github.com/" + path.lstrip("/"),
                                 headers={"Authorization": f"bearer {os.environ['GH_TOKEN']}", "User-Agent": "profile-stats",
                                          "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)
