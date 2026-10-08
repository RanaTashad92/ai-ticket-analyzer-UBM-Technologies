import re

CATEGORY_PATTERNS = {
    "Bug Report": [
        r"crash\w*", r"\bbugs?\b", r"\berrors?\b", r"broken", r"not working",
        r"doesn'?t work", r"does not work", r"\bfail\w*", r"freez\w*", r"\bstuck\b",
        r"glitch\w*", r"\bcan'?t\b", r"cannot", r"unable", r"won'?t (load|open)",
        r"blank screen", r"\bslow\b",
    ],
    "Billing Issue": [
        r"refund\w*", r"charged", r"\bcharges?\b", r"invoice\w*", r"billing",
        r"overcharg\w*", r"subscription", r"receipt", r"\bpricing\b", r"\bprice\b",
    ],
    "Feature Request": [
        r"\badd a\b", r"\badd an\b", r"please add", r"could you add",
        r"would be (awesome|nice|great|cool|helpful)", r"\bwish\b",
        r"feature request", r"\bsuggest\w*", r"support for", r"option to",
        r"would love", r"it would be",
    ],
    "General Inquiry": [
        r"how (do|can|to)", r"where (can|do)", r"\bis there\b", r"\bdo you\b",
        r"\bwhat is\b", r"\?",
    ],
}

TIE_ORDER = ["Bug Report", "Billing Issue", "Feature Request", "General Inquiry"]

URGENT_PATTERNS = [
    r"\basap\b", r"urgent\w*", r"immediately", r"right now", r"critical",
    r"emergency", r"production is down", r"losing money", r"data loss",
]

HIGH_PATTERNS = [
    r"crash\w*", r"charged twice", r"double charged", r"overcharg\w*", r"cannot",
    r"\bcan'?t\b", r"unable", r"security", r"hacked", r"locked out", r"refund\w*",
]

NEGATIVE_PATTERNS = [
    r"crash\w*", r"broken", r"\berrors?\b", r"\bfail\w*", r"terrible", r"worst",
    r"angry", r"frustrat\w*", r"disappoint\w*", r"unacceptable", r"not working",
    r"horrible", r"awful", r"useless", r"charged twice", r"double charged",
    r"overcharg\w*", r"\bbugs?\b", r"\bslow\b", r"can'?t", r"cannot", r"unable",
    r"\bfix\b",
]

POSITIVE_PATTERNS = [
    r"awesome", r"great", r"love\w*", r"amazing", r"excellent", r"fantastic",
    r"thank\w*", r"helpful", r"\bnice\b", r"perfect", r"wonderful", r"happy with",
]

PRODUCT_PATTERNS = [
    (r"payment page", "Payment Page"),
    (r"check-?out", "Checkout"),
    (r"dark mode", "Dark Mode"),
    (r"mobile app", "Mobile App"),
    (r"log-?in|sign-?in|password", "Login"),
    (r"dashboard", "Dashboard"),
    (r"notification\w*", "Notifications"),
    (r"subscription", "Subscription"),
    (r"invoice\w*", "Invoices"),
    (r"search", "Search"),
    (r"export\w*", "Export"),
    (r"report\w*", "Reports"),
    (r"\bapi\b", "API"),
    (r"\bapp\b", "App"),
    (r"website|web app", "Website"),
]

REPLY_TEMPLATES = {
    "Bug Report": "Hi, thank you for reporting the problem with {product}. We are sorry for the trouble. Our team is looking into it and will update you soon.",
    "Billing Issue": "Hi, thank you for contacting us about {product}. We are sorry for the confusion. Our billing team will review your account and reply shortly.",
    "Feature Request": "Hi, thank you for the suggestion about {product}. We have shared it with our product team and will let you know if it is planned.",
    "General Inquiry": "Hi, thank you for your message about {product}. A member of our team will get back to you with an answer soon.",
}


def _hits(text, patterns):
    return sum(1 for p in patterns if re.search(p, text))


def detect_category(text):
    scores = {c: _hits(text, p) for c, p in CATEGORY_PATTERNS.items()}
    best = max(scores.values())
    if best == 0:
        return "General Inquiry"
    for category in TIE_ORDER:
        if scores[category] == best:
            return category


def detect_sentiment(text):
    neg = _hits(text, NEGATIVE_PATTERNS)
    pos = _hits(text, POSITIVE_PATTERNS)
    if neg > pos:
        return "Negative"
    if pos > neg:
        return "Positive"
    return "Neutral"


def detect_priority(text, category):
    if _hits(text, URGENT_PATTERNS):
        return "Urgent"
    if category in ("Bug Report", "Billing Issue"):
        return "High" if _hits(text, HIGH_PATTERNS) else "Medium"
    if category == "Feature Request":
        return "Medium"
    return "Low"


def detect_product(text):
    earliest = None
    for pattern, label in PRODUCT_PATTERNS:
        match = re.search(pattern, text)
        if match and (earliest is None or match.start() < earliest[0]):
            earliest = (match.start(), label)
    return earliest[1] if earliest else "Not specified"


def build_reply(category, product):
    target = "your request" if product == "Not specified" else product
    return REPLY_TEMPLATES[category].format(product=target)


def analyze_with_rules(text):
    lowered = text.lower()
    category = detect_category(lowered)
    product = detect_product(lowered)
    return {
        "category": category,
        "priority": detect_priority(lowered, category),
        "sentiment": detect_sentiment(lowered),
        "product": product,
        "suggested_reply": build_reply(category, product),
    }