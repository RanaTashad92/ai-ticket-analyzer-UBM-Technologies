import re

FILLER_WORDS = {
    "hi", "hello", "hey", "hiya", "greetings", "yo", "sup", "good", "morning",
    "afternoon", "evening", "day", "team", "there", "all", "everyone", "dear",
    "sir", "madam", "hope", "you", "are", "have", "having", "a", "an", "nice",
    "great", "wonderful", "how", "is", "your", "doing", "well", "thanks",
    "thank", "regards", "best", "wishes", "happy", "new", "year", "the", "i",
    "am", "fine", "whats", "what", "up", "again", "so", "much", "very", "hows",
}

SPAM_PATTERNS = [
    r"\byou (have )?won\b",
    r"\bcongratulations\b",
    r"\bfree (gift|money|iphone|trial|vouchers?)\b",
    r"\bclaim your\b",
    r"\blottery\b",
    r"\bcrypto\b",
    r"\bearn \$?\d+",
    r"\bmake money\b",
    r"\bclick here\b",
    r"\bact now\b",
    r"\bviagra\b",
]

PROMO_PATTERNS = [
    r"\b\d{1,3}% off\b",
    r"\bpromo code\b",
    r"\blimited[- ]time\b",
    r"\bexclusive offer\b",
    r"\bsale ends\b",
    r"\bbuy now\b",
    r"\bdiscount\b",
    r"\bunsubscribe\b",
    r"\bour newsletter\b",
    r"\bspecial offer\b",
]


def _tokens(text):
    return re.findall(r"[a-z]+", text.lower().replace("'", ""))


def check_message(text):
    if text is None or not str(text).strip():
        return False, "empty message"

    cleaned = str(text).strip()
    lowered = cleaned.lower()

    for pattern in SPAM_PATTERNS:
        if re.search(pattern, lowered):
            return False, "spam"

    for pattern in PROMO_PATTERNS:
        if re.search(pattern, lowered):
            return False, "promotional broadcast"

    words = _tokens(cleaned)
    if len(words) <= 1:
        return False, "single word greeting"

    meaningful = [w for w in words if w not in FILLER_WORDS]
    if len(meaningful) < 2:
        return False, "greeting or small talk"

    return True, "qualifying"