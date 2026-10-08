import pytest

from analyzer.filters import check_message
from analyzer import llm
from analyzer.rules import analyze_with_rules


def test_ticket_one_bug_urgent_negative():
    r = analyze_with_rules("The payment page crashes every time I click 'Checkout' on Chrome. Please fix this ASAP!")
    assert r["category"] == "Bug Report"
    assert r["priority"] == "Urgent"
    assert r["sentiment"] == "Negative"


def test_ticket_two_feature_medium_positive():
    r = analyze_with_rules("Hi team, it would be awesome if you could add a dark mode to the mobile app.")
    assert r["category"] == "Feature Request"
    assert r["priority"] == "Medium"
    assert r["sentiment"] == "Positive"
    assert r["product"] == "Dark Mode"


@pytest.mark.parametrize(
    "text",
    ["Hello, hope you are having a nice day!", "hi", "", "Get 50% off today only", "You have won a free iPhone"],
)
def test_non_qualifying_messages_are_rejected(text):
    valid, _ = check_message(text)
    assert valid is False


def test_real_ticket_with_greeting_is_kept():
    valid, _ = check_message("Hi team, the app keeps freezing on login.")
    assert valid is True


def test_llm_valid_json_is_parsed(monkeypatch):
    raw = '{"category":"Bug Report","priority":"High","sentiment":"Negative","product":"Checkout","suggested_reply":"Sorry about that. We are on it."}'
    monkeypatch.setattr(llm, "_chat", lambda host, model, text: raw)
    result = llm.analyze_with_llm("http://localhost:11434", "llama3.2", "text")
    assert result["category"] == "Bug Report"


def test_llm_invalid_value_raises(monkeypatch):
    raw = '{"category":"Other","priority":"High","sentiment":"Negative","product":"X","suggested_reply":"Hi"}'
    monkeypatch.setattr(llm, "_chat", lambda host, model, text: raw)
    with pytest.raises(ValueError):
        llm.analyze_with_llm("http://localhost:11434", "llama3.2", "text")