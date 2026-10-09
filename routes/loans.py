from flask import Blueprint, request, jsonify
from db import get_db_connection

loans_bp = Blueprint("loans", __name__)


@loans_bp.route("", methods=["POST"])
def create_loan():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be JSON"}), 400

    book_id = data.get("book_id")
    reader_name = data.get("reader_name")
    loan_date = data.get("loan_date")

    if (
        type(book_id) is not int
        or book_id < 1
        or not isinstance(reader_name, str)
        or not reader_name.strip()
        or not isinstance(loan_date, str)
        or not loan_date.strip()
    ):
        return jsonify({
            "error": "book_id, reader_name and loan_date are required"
        }), 400

    conn = get_db_connection()
    try:
        book = conn.execute(
            "SELECT id FROM books WHERE id = ?", (book_id,)
        ).fetchone()

        if book is None:
            return jsonify({"error": "Book not found"}), 400

        active_loan = conn.execute("""
            SELECT id FROM loans
            WHERE book_id = ? AND returned = 0
        """, (book_id,)).fetchone()

        if active_loan is not None:
            return jsonify({
                "error": "Book is already on loan"
            }), 400

        cursor = conn.execute("""
            INSERT INTO loans (book_id, reader_name, loan_date)
            VALUES (?, ?, ?)
        """, (book_id, reader_name.strip(), loan_date.strip()))

        conn.commit()

        return jsonify({
            "id": cursor.lastrowid,
            "book_id": book_id,
            "reader_name": reader_name.strip(),
            "loan_date": loan_date.strip(),
            "returned": 0,
        }), 201
    finally:
        conn.close()


@loans_bp.route("/<int:loan_id>/return", methods=["PATCH"])
def return_loan(loan_id):
    conn = get_db_connection()
    try:
        loan = conn.execute(
            "SELECT * FROM loans WHERE id = ?", (loan_id,)
        ).fetchone()

        if loan is None:
            return jsonify({"error": "Loan not found"}), 404

        if loan["returned"] == 1:
            return jsonify({"error": "Already returned"}), 400

        conn.execute(
            "UPDATE loans SET returned = 1 WHERE id = ?",
            (loan_id,),
        )
        conn.commit()

        updated_loan = conn.execute(
            "SELECT * FROM loans WHERE id = ?", (loan_id,)
        ).fetchone()

        return jsonify(dict(updated_loan))
    finally:
        conn.close()


@loans_bp.route("/active", methods=["GET"])
def active_loans():
    conn = get_db_connection()
    try:
        rows = conn.execute("""
            SELECT
                loans.id AS loan_id,
                loans.reader_name,
                loans.loan_date,
                books.id AS book_id,
                books.title AS book_title,
                authors.name AS author_name
            FROM loans
            JOIN books ON loans.book_id = books.id
            JOIN authors ON books.author_id = authors.id
            WHERE loans.returned = 0
            ORDER BY loans.id
        """).fetchall()

        return jsonify([
            {
                "id": row["loan_id"],
                "reader_name": row["reader_name"],
                "loan_date": row["loan_date"],
                "book": {
                    "id": row["book_id"],
                    "title": row["book_title"],
                    "author_name": row["author_name"],
                },
            }
            for row in rows
        ])
    finally:
        conn.close()
