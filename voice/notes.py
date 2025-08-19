
import os
import json

def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def save_transcript(entry: dict, notes_dir: str = "notes", filename: str = "transcripts.jsonl"):
    """
    Append a transcript entry to a JSONL file.
    Each line: {"timestamp": "...", "file": "...", "text": "..."}
    """
    _ensure_dir(notes_dir)
    out_path = os.path.join(notes_dir, filename)
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
