from flask import Blueprint, request, jsonify
from db import get_db_connection

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/overview", methods=["GET"])
def overview():
    conn = get_db_connection()
    try:
        authors_count = conn.execute(
            "SELECT COUNT(*) FROM authors"
        ).fetchone()[0]

        books_count = conn.execute(
            "SELECT COUNT(*) FROM books"
        ).fetchone()[0]

        active_loans_count = conn.execute(
            "SELECT COUNT(*) FROM loans WHERE returned = 0"
        ).fetchone()[0]

        return jsonify({
            "authors_count": authors_count,
            "books_count": books_count,
            "active_loans_count": active_loans_count,
        })
    finally:
        conn.close()


@stats_bp.route("/top-genres", methods=["GET"])
def top_genres():
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT genre, COUNT(*) AS books_count
            FROM books
            GROUP BY genre
            ORDER BY books_count DESC, genre
            LIMIT 3
        """).fetchall()

        return jsonify([dict(row) for row in rows])
    finally:
        conn.close()
