import csv
import json
import sqlite3
from pathlib import Path

RESULT_FIELDS = [
    "id", "message", "category", "priority", "sentiment",
    "product", "suggested_reply", "method",
]
REJECTED_FIELDS = ["id", "message", "reason"]


def save_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def save_json(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)


def save_sqlite(path, results, rejected):
    conn = sqlite3.connect(path)
    conn.execute("DROP TABLE IF EXISTS tickets")
    conn.execute("DROP TABLE IF EXISTS rejected")
    conn.execute(
        """CREATE TABLE tickets (
            id TEXT PRIMARY KEY,
            message TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            product TEXT NOT NULL,
            suggested_reply TEXT NOT NULL,
            method TEXT NOT NULL
        )"""
    )
    conn.execute(
        "CREATE TABLE rejected (id TEXT PRIMARY KEY, message TEXT, reason TEXT NOT NULL)"
    )
    conn.executemany(
        "INSERT INTO tickets VALUES (:id, :message, :category, :priority, "
        ":sentiment, :product, :suggested_reply, :method)",
        results,
    )
    conn.executemany(
        "INSERT INTO rejected VALUES (:id, :message, :reason)", rejected
    )
    conn.commit()
    conn.close()


def save_all(output_dir, results, rejected):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    save_csv(out / "results.csv", results, RESULT_FIELDS)
    save_json(out / "results.json", results)
    save_csv(out / "rejected.csv", rejected, REJECTED_FIELDS)
    save_sqlite(out / "tickets.db", results, rejected)