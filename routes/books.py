from flask import Blueprint, request, jsonify
from db import get_db_connection

books_bp = Blueprint("books", __name__)


@books_bp.route("", methods=["GET"])
def get_books():
    genre = request.args.get("genre")
    author_id = request.args.get("author_id")

    conditions = []
    params = []

    if genre:
        conditions.append("books.genre = ?")
        params.append(genre)

    if author_id:
        try:
            author_id = int(author_id)
            if author_id < 1:
                raise ValueError
        except ValueError:
            return jsonify({"error": "Invalid author_id"}), 400

        conditions.append("books.author_id = ?")
        params.append(author_id)

    sql = """
        SELECT
            books.id,
            books.title,
            books.genre,
            books.year,
            authors.id AS author_id,
            authors.name AS author_name,
            authors.country AS author_country
        FROM books
        JOIN authors ON books.author_id = authors.id
    """

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY books.id"

    conn = get_db_connection()
    try:
        rows = conn.execute(sql, params).fetchall()
        return jsonify([
            {
                "id": row["id"],
                "title": row["title"],
                "genre": row["genre"],
                "year": row["year"],
                "author": {
                    "id": row["author_id"],
                    "name": row["author_name"],
                    "country": row["author_country"],
                },
            }
            for row in rows
        ])
    finally:
        conn.close()


@books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    conn = get_db_connection()
    try:
        row = conn.execute("""
            SELECT
                books.id,
                books.title,
                books.genre,
                books.year,
                authors.id AS author_id,
                authors.name AS author_name,
                authors.country AS author_country
            FROM books
            JOIN authors ON books.author_id = authors.id
            WHERE books.id = ?
        """, (book_id,)).fetchone()

        if row is None:
            return jsonify({"error": "Book not found"}), 404

        return jsonify({
            "id": row["id"],
            "title": row["title"],
            "genre": row["genre"],
            "year": row["year"],
            "author": {
                "id": row["author_id"],
                "name": row["author_name"],
                "country": row["author_country"],
            },
        })
    finally:
        conn.close()


@books_bp.route("", methods=["POST"])
def add_book():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be JSON"}), 400

    title = data.get("title")
    genre = data.get("genre")
    year = data.get("year")
    author_id = data.get("author_id")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "Title is required"}), 400

    if not isinstance(genre, str) or not genre.strip():
        return jsonify({"error": "Genre is required"}), 400

    if year is not None and type(year) is not int:
        return jsonify({"error": "Year must be an integer or null"}), 400

    if type(author_id) is not int or author_id < 1:
        return jsonify({"error": "Valid author_id is required"}), 400

    conn = get_db_connection()
    try:
        author = conn.execute(
            "SELECT id FROM authors WHERE id = ?", (author_id,)
        ).fetchone()

        if author is None:
            return jsonify({"error": "Author not found"}), 400

        cursor = conn.execute("""
            INSERT INTO books (title, genre, year, author_id)
            VALUES (?, ?, ?, ?)
        """, (title.strip(), genre.strip(), year, author_id))

        conn.commit()
        book_id = cursor.lastrowid
        
        return jsonify({
            "id": book_id,
            "title": title.strip(),
            "genre": genre.strip(),
            "year": year,
            "author_id": author_id,
        }), 201
    finally:
        conn.close()


@books_bp.route("/popular", methods=["GET"])
def popular_books():
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT
                books.id,
                books.title,
                books.genre,
                COUNT(loans.id) AS loans_count
            FROM books
            LEFT JOIN loans ON loans.book_id = books.id
            GROUP BY books.id
            ORDER BY loans_count DESC, books.id
            LIMIT 3
        """).fetchall()

        return jsonify([dict(row) for row in rows])
    finally:
        conn.close()
