# scoreboard.py

import json
import os

# Project root (parent of src/), independent of the working directory.
SCOREBOARD_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scoreboard.json"
)
MAX_ENTRIES = 20

def _valid_entry(e):
    return (
        isinstance(e, dict)
        and isinstance(e.get("name"), str)
        and isinstance(e.get("score"), (int, float))
        and not isinstance(e.get("score"), bool)
    )

def load_scoreboard():
    """
    Reads scoreboard from scoreboard.json.
    Returns a list of dicts: [{ "name": "ABC", "score": 99 }, ...]
    Missing, unreadable or malformed data yields [] / only the valid entries.
    """
    try:
        with open(SCOREBOARD_FILE, "r") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    return [e for e in data if _valid_entry(e)]

def save_scoreboard(entries):
    """
    Writes the scoreboard list to scoreboard.json (atomically via a temp file).
    Each entry is a dict with {"name": str, "score": int}.
    Returns True on success, False if the file could not be written.
    """
    tmp = SCOREBOARD_FILE + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump(entries, f)
        os.replace(tmp, SCOREBOARD_FILE)
        return True
    except OSError:
        return False

def add_score(name, score):
    """
    Loads scoreboard, adds a new entry, sorts by highest score,
    then keeps only up to MAX_ENTRIES. Returns updated list.
    """
    entries = load_scoreboard()
    entries.append({"name": name, "score": score})

    # Sort descending by score
    entries.sort(key=lambda x: x["score"], reverse=True)
    # Keep top MAX_ENTRIES
    entries = entries[:MAX_ENTRIES]

    save_scoreboard(entries)
    return entries
