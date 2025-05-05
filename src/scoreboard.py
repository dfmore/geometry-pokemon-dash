# scoreboard.py

import json
import os

SCOREBOARD_FILE = "scoreboard.json"
MAX_ENTRIES = 20

def load_scoreboard():
    """
    Reads scoreboard from scoreboard.json.
    Returns a list of dicts: [{ "name": "ABC", "score": 99 }, ...]
    """
    if not os.path.exists(SCOREBOARD_FILE):
        return []
    with open(SCOREBOARD_FILE, "r") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
        except json.JSONDecodeError:
            return []

def save_scoreboard(entries):
    """
    Writes the scoreboard list to scoreboard.json.
    Each entry is a dict with {"name": str, "score": int}
    """
    with open(SCOREBOARD_FILE, "w") as f:
        json.dump(entries, f)

def add_score(name, score):
    """
    Loads scoreboard, adds a new entry, sorts by highest score,
    then keeps only up to MAX_ENTRIES. Returns updated list.
    """
    entries = load_scoreboard()
    entries.append({"name": name, "score": score})

    # Sort descending by score
    entries.sort(key=lambda x: x["score"], reverse=True)
    # Keep top 5
    entries = entries[:MAX_ENTRIES]

    save_scoreboard(entries)
    return entries
