import csv
import json
import os
from pathlib import Path

from .filters import check_message
from .llm import analyze_with_llm, ollama_ready
from .rules import analyze_with_rules
from .storage import save_all

DEFAULT_MODEL = "llama3"
DEFAULT_HOST = "http://localhost:11434"


def load_messages(path):
    path = Path(path)
    if path.suffix.lower() == ".json":
        with open(path, encoding="utf-8") as f:
            records = json.load(f)
    else:
        with open(path, newline="", encoding="utf-8") as f:
            records = list(csv.DictReader(f))
    messages = []
    for index, record in enumerate(records, start=1):
        messages.append(
            {
                "id": str(record.get("id") or index),
                "message": str(record.get("message") or "").strip(),
            }
        )
    return messages


def analyze_message(text, use_llm, host, model):
    if use_llm:
        try:
            return analyze_with_llm(host, model, text), "llm"
        except Exception:
            pass
    return analyze_with_rules(text), "rules"


def run(input_path, output_dir, offline=False):
    model = os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL)
    host = os.environ.get("OLLAMA_HOST", DEFAULT_HOST)
    use_llm = (not offline) and ollama_ready(host, model)
    mode = f"Ollama ({model})" if use_llm else "Rules only"

    results, rejected = [], []
    for item in load_messages(input_path):
        valid, reason = check_message(item["message"])
        if not valid:
            rejected.append({**item, "reason": reason})
            continue
        analysis, method = analyze_message(item["message"], use_llm, host, model)
        results.append({**item, **analysis, "method": method})

    save_all(output_dir, results, rejected)
    return results, rejected, mode