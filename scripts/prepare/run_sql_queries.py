"""Run the documented hypothesis queries against the generated SQLite DB."""

from pathlib import Path
import sqlite3

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATABASE = ROOT / "build" / "dodgers_analysis.db"
QUERY_FILE = ROOT / "sql" / "hypothesis_queries.sql"


def split_queries(sql: str) -> list[tuple[str, str]]:
    queries: list[tuple[str, str]] = []
    title: str | None = None
    buffer: list[str] = []
    for line in sql.splitlines():
        if line.startswith("-- Q"):
            if title is not None and buffer and "".join(buffer).strip():
                queries.append((title, "\n".join(buffer)))
            buffer = []
            title = line[3:].strip()
        elif title is not None:
            buffer.append(line)
    if title is not None and "".join(buffer).strip():
        queries.append((title, "\n".join(buffer)))
    return queries


def main() -> None:
    if not DATABASE.exists():
        raise SystemExit("Database missing. Run: python scripts/prepare/build_sqlite_db.py")
    sql = QUERY_FILE.read_text(encoding="utf-8")
    with sqlite3.connect(DATABASE) as connection:
        for title, query in split_queries(sql):
            query = query.strip()
            if not query:
                continue
            print(f"\n{'=' * 20} {title} {'=' * 20}")
            print(pd.read_sql_query(query, connection).to_string(index=False))


if __name__ == "__main__":
    main()
