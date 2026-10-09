import sqlite3


def seed_db():
    conn = sqlite3.connect("library.db")
    conn.execute("PRAGMA foreign_keys = ON")

    conn.executescript("""
        DROP TABLE IF EXISTS loans;
        DROP TABLE IF EXISTS books;
        DROP TABLE IF EXISTS authors;

        CREATE TABLE authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT
        );

        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            year INTEGER,
            author_id INTEGER NOT NULL,
            FOREIGN KEY (author_id)
                REFERENCES authors(id)
                ON DELETE CASCADE
        );

        CREATE TABLE loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            reader_name TEXT NOT NULL,
            loan_date TEXT NOT NULL,
            returned INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (book_id)
                REFERENCES books(id)
                ON DELETE CASCADE
        );
    """)

    conn.executemany(
        "INSERT INTO authors (name, country) VALUES (?, ?)",
        [
            ("Джоан Роулинг", "United Kingdom"),
            ("Стивен Кинг", "United States"),
            ("Александр Дюма", "France")
        ]
    )

    conn.executemany(
        """INSERT INTO books (title, genre, year, author_id)
           VALUES (?, ?, ?, ?)""",
        [
            ("Гарри Поттер и философский камень", "fantasy", 1997, 1),
            ("Гарри Поттер и Тайная комната", "fantasy", 1998, 1),
            ("Оно", "horror", 1986, 2),
            ("Зелёная миля", "drama", 1996, 2),
            ("Три мушкетёра", "adventure", 1844, 3),
            ("Граф Монте-Кристо", "adventure", 1844, 3)
        ]
    )

    conn.executemany(
        """INSERT INTO loans
           (book_id, reader_name, loan_date, returned)
           VALUES (?, ?, ?, ?)""",
        [
            (1, "Азиз", "2026-10-01", 0),
            (2, "Мухаммад", "2026-10-02", 1),
            (3, "Алишер", "2026-10-03", 0),
            (5, "Фирдавс", "2026-10-04", 1)
        ]
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_db()