import sqlite3
from pathlib import Path
from datetime import datetime, timezone

class Database:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn
    def initialize(self):
        with self.connect() as c:
            c.executescript(
                "CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY, name TEXT NOT NULL, content TEXT NOT NULL, content_hash TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL);"
                "CREATE TABLE IF NOT EXISTS summaries(id INTEGER PRIMARY KEY, document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE, method TEXT NOT NULL, summary TEXT NOT NULL, created_at TEXT NOT NULL);"
                "CREATE TABLE IF NOT EXISTS questions(id INTEGER PRIMARY KEY, document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE, question TEXT NOT NULL, answer TEXT NOT NULL, evidence TEXT NOT NULL, created_at TEXT NOT NULL);"
            )
    @staticmethod
    def now():
        return datetime.now(timezone.utc).isoformat(timespec="seconds")
    def add_document(self, name, content, content_hash):
        with self.connect() as c:
            row = c.execute("SELECT id FROM documents WHERE content_hash=?", (content_hash,)).fetchone()
            if row:
                return int(row["id"])
            cur = c.execute("INSERT INTO documents(name,content,content_hash,created_at) VALUES(?,?,?,?)", (name,content,content_hash,self.now()))
            return int(cur.lastrowid)
    def get_document(self, doc_id):
        with self.connect() as c:
            row = c.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
            return dict(row) if row else None
    def list_documents(self):
        with self.connect() as c:
            return [dict(r) for r in c.execute("SELECT id,name,created_at,length(content) AS chars FROM documents ORDER BY id DESC")]
    def add_summary(self, doc_id, method, summary):
        with self.connect() as c:
            c.execute("INSERT INTO summaries(document_id,method,summary,created_at) VALUES(?,?,?,?)", (doc_id,method,summary,self.now()))
    def add_question(self, doc_id, question, answer, evidence):
        with self.connect() as c:
            c.execute("INSERT INTO questions(document_id,question,answer,evidence,created_at) VALUES(?,?,?,?,?)", (doc_id,question,answer,evidence,self.now()))
    def history(self, doc_id):
        with self.connect() as c:
            s = c.execute("SELECT * FROM summaries WHERE document_id=? ORDER BY id DESC", (doc_id,)).fetchall()
            q = c.execute("SELECT * FROM questions WHERE document_id=? ORDER BY id DESC", (doc_id,)).fetchall()
            return {"summaries":[dict(x) for x in s], "questions":[dict(x) for x in q]}
