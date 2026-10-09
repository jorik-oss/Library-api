from flask import Blueprint, request,jsonify
from db import get_db_connection

authors_bp = Blueprint("authors", __name__)


@authors_bp.route("", methods=["GET"])
def get_authors():
    conn = get_db_connection()
    try:
        rows = conn.execute(
            "SELECT id, name, country FROM authors ORDER BY id"
        ).fetchall()
        return jsonify([dict(row) for row in rows])
    finally:
        conn.close()


@authors_bp.route("/<int:author_id>", methods=["GET"])
def get_author(author_id):
    conn = get_db_connection()
    try:
        row = conn.execute(
            "SELECT id, name, country FROM authors WHERE id = ?",
            (author_id,),
        ).fetchone()

        if row is None:
            return jsonify({"error": "Author not found"}), 404

        return jsonify(dict(row))
    finally:
        conn.close()


@authors_bp.route("/stats", methods=["GET"])
def author_stats():
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT
                authors.id,
                authors.name,
                authors.country,
                COUNT(DISTINCT books.id) AS books_count,
                COUNT(loans.id) AS loans_count
            FROM authors
            LEFT JOIN books ON books.author_id = authors.id
            LEFT JOIN loans ON loans.book_id = books.id
            GROUP BY authors.id
            ORDER BY authors.id
        """).fetchall()

        return jsonify([dict(row) for row in rows])
    finally:
        conn.close()


@authors_bp.route("/<int:author_id>", methods=["DELETE"])
def delete_author(author_id):
    conn = get_db_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM authors WHERE id = ?", (author_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Author not found"}), 404

        conn.commit()
        return jsonify({"message": "Author deleted successfully"})
    finally:
        conn.close()
