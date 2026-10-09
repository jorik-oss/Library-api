from flask import Flask

from routes.books import books_bp
from routes.authors import authors_bp
from routes.loans import loans_bp
from routes.stats import stats_bp


def create_app():
    app = Flask(__name__)

    app.register_blueprint(books_bp, url_prefix="/books")
    app.register_blueprint(authors_bp, url_prefix="/authors")
    app.register_blueprint(loans_bp, url_prefix="/loans")
    app.register_blueprint(stats_bp, url_prefix="/stats")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
