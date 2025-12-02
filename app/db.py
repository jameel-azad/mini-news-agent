import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / 'news.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                published_at TEXT,
                source TEXT,
                UNIQUE(company_id, url),
                FOREIGN KEY (company_id) REFERENCES companies(id)
            );
            """
        )

        conn.commit()

def get_or_create_company(name:str)->int:
    name = name.strip()
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("SELECT id FROM COMPANIES WHERE name = ?;",(name,))
        row = cur.fetchone()
        if row is not None:
            return row['id']
        
        cur.execute("INSERT INTO COMPANIES (name) VALUES (?);", (name,))
        conn.commit()
        return cur.lastrowid

def insert_news_items(company_name:str, items:list[dict])->int:
    if not items:
        return 0
    
    company_id = get_or_create_company(company_name)

    inserted = 0

    with get_connection() as conn:
        cur = conn.cursor()
        for item in items:
            try:
                cur.execute(
                    """
                    INSERT OR IGNORE INTO news (company_id, title, url, published_at, source)
                    VALUES (?,?,?,?,?);
                    """,
                    (
                        company_id,
                        item.get("title", "").strip(),
                        item.get("url", "").strip(),
                        item.get("published_at", ""),
                        item.get("source", "").strip(),
                    ),
                )
                if cur.rowcount > 0:
                    inserted += 1
            except Exception as e:
                print("Error inserting news item:",e)

        conn.commit()
    return inserted

def get_news_by_company(company_name: str, limit: int = 10) -> list[dict]:
    company_name = company_name.strip()
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("SELECT id FROM companies WHERE name = ?;", (company_name,))
        row = cur.fetchone()
        if row is None:
            return []

        company_id = row["id"]

        cur.execute(
            """
            SELECT title, url, published_at, source
            FROM news
            WHERE company_id = ?
            ORDER BY published_at DESC
            LIMIT ?;
            """,
            (company_id, limit),
        )
        rows = cur.fetchall()

    return [
        {
            "company": company_name,
            "title": r["title"],
            "url": r["url"],
            "published_at": r["published_at"],
            "source": r["source"],
        }
        for r in rows
    ]

if __name__ == "__main__":
    init_db()
    cid = get_or_create_company("Toyota")
    print("Company ID:", cid)

    # Fake insert test
    sample_items = [
        {
            "company": "Toyota",
            "title": "Test news item",
            "url": "https://example.com/test",
            "published_at": "2025-12-01T00:00:00Z",
            "source": "Example Source",
        }
    ]
    inserted = insert_news_items("Toyota", sample_items)
    print("Inserted rows:", inserted)

    rows = get_news_by_company("Toyota", limit=5)
    print("From DB:")
    for r in rows:
        print("-", r["title"], "->", r["url"])