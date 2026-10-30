import os
import sqlite3


class FirstbreathDatabase:
    def __init__(self, db_path="firstbreath_substrate.db"):
        self.db_path = db_path
        parent_dir = os.path.dirname(os.path.abspath(self.db_path))
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        self.conn = None
        self.initialize_storage()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path, timeout=30.0)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode = WAL;")
        self.conn.execute("PRAGMA synchronous = NORMAL;")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        return self.conn

    def initialize_storage(self):
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_state (
                agent_id TEXT PRIMARY KEY,
                state_vector TEXT,
                timestamp REAL,
                metadata TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS session_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_key TEXT,
                event_data TEXT,
                timestamp REAL
            )
            """
        )
        self.conn.commit()
        cursor.close()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
