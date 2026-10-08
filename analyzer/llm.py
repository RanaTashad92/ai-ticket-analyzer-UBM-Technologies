import json
import re
import urllib.request

CATEGORIES = ["Bug Report", "Feature Request", "Billing Issue", "General Inquiry"]
PRIORITIES = ["Low", "Medium", "High", "Urgent"]
SENTIMENTS = ["Positive", "Neutral", "Negative"]

SYSTEM_PROMPT = (
    "You analyze customer support messages. Reply with one JSON object only, "
    "no extra text. Keys: category (one of Bug Report, Feature Request, Billing Issue, "
    "General Inquiry), priority (one of Low, Medium, High, Urgent), sentiment "
    "(one of Positive, Neutral, Negative), product (the main product or feature "
    "named in the message, or Not specified), suggested_reply (a short, polite "
    "reply of at most two sentences). Use Urgent only when the customer shows "
    "real urgency such as ASAP or immediately."
)


def ollama_ready(host, model):
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=3) as resp:
            names = [m["name"] for m in json.load(resp).get("models", [])]
    except Exception:
        return False
    return any(name == model or name.startswith(model + ":") for name in names)


def _chat(host, model, text):
    payload = json.dumps(
        {
            "model": model,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{host}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=120) as resp:
        body = json.load(resp)
    return body["message"]["content"]


def _parse(raw):
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    data = json.loads(cleaned)
    if data.get("category") not in CATEGORIES:
        raise ValueError("invalid category")
    if data.get("priority") not in PRIORITIES:
        raise ValueError("invalid priority")
    if data.get("sentiment") not in SENTIMENTS:
        raise ValueError("invalid sentiment")
    if not data.get("product") or not data.get("suggested_reply"):
        raise ValueError("missing fields")
    return {
        "category": data["category"],
        "priority": data["priority"],
        "sentiment": data["sentiment"],
        "product": str(data["product"]).strip(),
        "suggested_reply": str(data["suggested_reply"]).strip(),
    }


def analyze_with_llm(host, model, text):
    return _parse(_chat(host, model, text))