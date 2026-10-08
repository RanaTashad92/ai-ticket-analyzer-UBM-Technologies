# AI-Powered Customer Feedback & Support Ticket Analyzer

A Python-based automated system that processes customer support tickets, filters out non-qualifying messages (spam, greetings, promotions), classifies valid tickets by intent, priority, and sentiment using AI, and outputs structured results into CSV, JSON, and SQLite.

## Overview

Customer support teams receive thousands of messages daily — many of which are spam, greetings, or promotional content. This tool automates the triage process:

1. **Reads** customer messages from a CSV or JSON file
2. **Filters** out non-qualifying messages (spam, single-word greetings, promotional broadcasts, small talk)
3. **Analyzes** each valid ticket to extract:
   - **Category** — Bug Report, Feature Request, Billing Issue, or General Inquiry
   - **Priority** — Low, Medium, High, or Urgent
   - **Sentiment** — Positive, Neutral, or Negative
   - **Product/Feature** — The main product or feature mentioned in the message
   - **Suggested Reply** — A short, polite auto-generated response
4. **Stores** the structured results into multiple output formats (CSV, JSON, SQLite)

## Architecture

```
data/tickets.csv
       │
       ▼
  ┌──────────┐
  │  Filter   │──→ rejected.csv (spam, greetings, promos)
  └────┬─────┘
       │ valid tickets
       ▼
  ┌──────────┐     ┌───────────┐
  │ Analyzer  │────▶│ Ollama LLM│ (if available)
  │          │     └───────────┘
  │          │     ┌───────────┐
  │          │────▶│ Rules Engine│ (regex fallback)
  └────┬─────┘     └───────────┘
       │
       ▼
  ┌──────────┐
  │  Storage  │──→ results.csv, results.json, tickets.db
  └──────────┘
```

The system supports **two analysis modes**:
- **LLM Mode** (default): Sends each ticket to a locally running Ollama model (e.g., `llama3`) for AI-powered classification. Produces more nuanced and context-aware results.
- **Rules Mode** (offline fallback): Uses regex pattern matching to classify tickets. Requires no external services and runs instantly.

If Ollama is not running or the model is unavailable, the system **automatically falls back** to rules mode.

## Setup & Installation

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) (optional, for LLM mode)

### Install

```bash
git clone https://github.com/RanaTashad92/ai-ticket-analyzer-UBM-Technologies.git
cd ai-ticket-analyzer-UBM-Technologies
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Run with Rules Engine (no Ollama required)

```bash
python main.py --offline
```

### Run with Ollama LLM

```bash
ollama pull llama3
$env:OLLAMA_MODEL="llama3"
python main.py
```

### Custom Input File

```bash
python main.py --input path/to/your/tickets.csv --output-dir output
```

The input file should be a CSV or JSON with `id` and `message` columns.

### CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | `data/tickets.csv` | Path to input CSV or JSON file |
| `--output-dir` | `output` | Directory to save results |
| `--offline` | `False` | Force rules-only mode (skip LLM) |

## Sample Input & Output

### Input (`data/tickets.csv`)

| ID | Message |
|----|---------|
| 1 | "The payment page crashes every time I click 'Checkout' on Chrome. Please fix this ASAP!" |
| 2 | "Hi team, it would be awesome if you could add a dark mode to the mobile app." |
| 3 | "Hello, hope you are having a nice day!" |
| 4 | "hi" |
| 5 | "I was charged twice for my subscription this month. Please refund the extra payment." |
| 6 | "CONGRATULATIONS! You have won a free iPhone. Click here to claim your prize." |

### Output — Analyzed Tickets

| ID | Category | Priority | Sentiment | Product | Method |
|----|----------|----------|-----------|---------|--------|
| 1 | Bug Report | Urgent | Negative | Payment Page | rules |
| 2 | Feature Request | Medium | Positive | Dark Mode | rules |
| 5 | Billing Issue | High | Negative | Subscription | rules |

### Output — Rejected Messages

| ID | Message | Reason |
|----|---------|--------|
| 3 | "Hello, hope you are having a nice day!" | greeting or small talk |
| 4 | "hi" | single word greeting |
| 6 | "CONGRATULATIONS! You have won a free iPhone..." | spam |

## Output Files

After running, the `output/` directory contains:

| File | Format | Contents |
|------|--------|----------|
| `results.csv` | CSV | All analyzed tickets with category, priority, sentiment, product, and suggested reply |
| `results.json` | JSON | Same data in JSON format |
| `rejected.csv` | CSV | Filtered-out messages with rejection reasons |
| `tickets.db` | SQLite | Database with `tickets` and `rejected` tables |

## Filtering Logic

Messages are rejected if they match any of the following:

| Filter | Examples |
|--------|----------|
| **Empty** | Blank or whitespace-only messages |
| **Spam** | "You have won", "Free iPhone", "Click here", "Earn $500" |
| **Promotional** | "50% off", "Promo code", "Limited time offer", "Unsubscribe" |
| **Single Word** | "hi", "hello", "hey" |
| **Small Talk** | "Hello, hope you are having a nice day!" (fewer than 2 meaningful words after removing filler) |

## Testing

```bash
python -m pytest tests/ -v
```

Tests cover:
- Ticket 1 correctly classified as Bug Report / Urgent / Negative
- Ticket 2 correctly classified as Feature Request / Medium / Positive
- Non-qualifying messages (greetings, spam, promos) are rejected
- Real tickets with greetings prefix ("Hi team, the app keeps freezing...") are kept
- LLM JSON response parsing and validation
- Invalid LLM responses raise appropriate errors

## Project Structure

```
ai-ticket-analyzer/
├── main.py                  # CLI entry point with argparse
├── requirements.txt         # Python dependencies
├── analyzer/
│   ├── __init__.py
│   ├── filters.py           # Message filtering (spam, greetings, promos)
│   ├── llm.py               # Ollama LLM integration & response parsing
│   ├── rules.py             # Regex-based rule engine (offline fallback)
│   ├── pipeline.py          # Orchestrator — load, filter, analyze, store
│   └── storage.py           # Multi-format output (CSV, JSON, SQLite)
├── data/
│   └── tickets.csv          # Sample input data (18 test tickets)
├── tests/
│   └── test_pipeline.py     # Unit tests (pytest)
└── output/                  # Generated results (created on first run)
```

## Technologies Used

- **Python 3** — Core language
- **Ollama** — Local LLM inference (llama3)
- **SQLite** — Structured database storage
- **pytest** — Unit testing
- **Standard Library** — csv, json, re, urllib, argparse, sqlite3 (no heavy dependencies)
