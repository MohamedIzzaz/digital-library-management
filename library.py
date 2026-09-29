"""Core logic for the Digital Library Management System (SQLite backed)."""
import sqlite3
from datetime import date, timedelta

DB_FILE = "library.db"
LOAN_DAYS = 14      # days a book can be borrowed
FINE_PER_DAY = 2    # fine per overdue day (currency units)


class Library:
    def __init__(self, db_file=DB_FILE):
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS books (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                title     TEXT NOT NULL,
                author    TEXT NOT NULL,
                isbn      TEXT UNIQUE NOT NULL,
                copies    INTEGER NOT NULL CHECK (copies >= 0),
                available INTEGER NOT NULL CHECK (available >= 0)
            );
            CREATE TABLE IF NOT EXISTS members (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            );
            CREATE TABLE IF NOT EXISTS loans (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id     INTEGER NOT NULL REFERENCES books(id),
                member_id   INTEGER NOT NULL REFERENCES members(id),
                issue_date  TEXT NOT NULL,
                due_date    TEXT NOT NULL,
                return_date TEXT,
                fine        INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        self.conn.commit()

    # ---------- Books ----------
    def add_book(self, title, author, isbn, copies=1):
        if not title.strip() or not author.strip() or not isbn.strip():
            raise ValueError("Title, author and ISBN are required.")
        if copies < 1:
            raise ValueError("Copies must be at least 1.")
        try:
            cur = self.conn.execute(
                "INSERT INTO books (title, author, isbn, copies, available) "
                "VALUES (?, ?, ?, ?, ?)",
                (title.strip(), author.strip(), isbn.strip(), copies, copies),
            )
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("A book with this ISBN already exists.")

    def list_books(self):
        return self.conn.execute("SELECT * FROM books ORDER BY title").fetchall()

    def search_books(self, keyword):
        like = f"%{keyword.strip()}%"
        return self.conn.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? "
            "ORDER BY title",
            (like, like, like),
        ).fetchall()

    def remove_book(self, book_id):
        if not self._get_book(book_id):
            raise ValueError("Book not found.")
        used = self.conn.execute(
            "SELECT COUNT(*) FROM loans WHERE book_id = ?", (book_id,)
        ).fetchone()[0]
        if used:
            raise ValueError("Cannot remove a book that has loan history.")
        self.conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        self.conn.commit()

    # ---------- Members ----------
    def add_member(self, name, email):
        if not name.strip() or "@" not in email:
            raise ValueError("A valid name and email are required.")
        try:
            cur = self.conn.execute(
                "INSERT INTO members (name, email) VALUES (?, ?)",
                (name.strip(), email.strip().lower()),
            )
            self.conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError("A member with this email already exists.")

    def list_members(self):
        return self.conn.execute("SELECT * FROM members ORDER BY name").fetchall()

    # ---------- Loans ----------
    def issue_book(self, book_id, member_id, today=None):
        today = today or date.today()
        book = self._get_book(book_id)
        if not book:
            raise ValueError("Book not found.")
        if not self.conn.execute(
            "SELECT 1 FROM members WHERE id = ?", (member_id,)
        ).fetchone():
            raise ValueError("Member not found.")
        if book["available"] < 1:
            raise ValueError("No copies available right now.")
        already = self.conn.execute(
            "SELECT 1 FROM loans WHERE book_id=? AND member_id=? AND return_date IS NULL",
            (book_id, member_id),
        ).fetchone()
        if already:
            raise ValueError("This member already has this book.")
        due = today + timedelta(days=LOAN_DAYS)
        cur = self.conn.execute(
            "INSERT INTO loans (book_id, member_id, issue_date, due_date) "
            "VALUES (?, ?, ?, ?)",
            (book_id, member_id, today.isoformat(), due.isoformat()),
        )
        self.conn.execute(
            "UPDATE books SET available = available - 1 WHERE id = ?", (book_id,)
        )
        self.conn.commit()
        return cur.lastrowid, due

    def return_book(self, loan_id, today=None):
        today = today or date.today()
        loan = self.conn.execute(
            "SELECT * FROM loans WHERE id = ?", (loan_id,)
        ).fetchone()
        if not loan:
            raise ValueError("Loan not found.")
        if loan["return_date"]:
            raise ValueError("This book was already returned.")
        due = date.fromisoformat(loan["due_date"])
        fine = max((today - due).days, 0) * FINE_PER_DAY
        self.conn.execute(
            "UPDATE loans SET return_date = ?, fine = ? WHERE id = ?",
            (today.isoformat(), fine, loan_id),
        )
        self.conn.execute(
            "UPDATE books SET available = available + 1 WHERE id = ?",
            (loan["book_id"],),
        )
        self.conn.commit()
        return fine

    def list_loans(self, active_only=True):
        query = (
            "SELECT l.id, b.title, m.name AS member, l.issue_date, l.due_date, "
            "l.return_date, l.fine FROM loans l "
            "JOIN books b ON b.id = l.book_id JOIN members m ON m.id = l.member_id "
        )
        if active_only:
            query += "WHERE l.return_date IS NULL "
        query += "ORDER BY l.id"
        return self.conn.execute(query).fetchall()

    def _get_book(self, book_id):
        return self.conn.execute(
            "SELECT * FROM books WHERE id = ?", (book_id,)
        ).fetchone()

    def close(self):
        self.conn.close()
