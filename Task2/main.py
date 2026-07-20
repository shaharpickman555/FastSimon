import logging
import os

from flask import Flask, Response, render_template, request

from store import Database


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)


def create_app(database=None):
    app = Flask(__name__)
    db = database or Database()

    def text(body, status=200):
        return Response(f"{body}\n", status=status, mimetype="text/plain")

    def param(name):
        value = request.args.get(name)
        if value is None or value == "" or " " in value:
            raise ValueError(f"missing or invalid '{name}'")
        return value

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/set")
    def set_value():
        try:
            name = param("name")
            value = param("value")
        except ValueError as error:
            logger.warning("Bad SET request: %s", error)
            return text(f"ERROR: {error}", 400)
        return text(db.set(name, value))

    @app.get("/get")
    def get_value():
        try:
            name = param("name")
        except ValueError as error:
            logger.warning("Bad GET request: %s", error)
            return text(f"ERROR: {error}", 400)
        return text(db.get(name))

    @app.get("/unset")
    def unset_value():
        try:
            name = param("name")
        except ValueError as error:
            logger.warning("Bad UNSET request: %s", error)
            return text(f"ERROR: {error}", 400)
        return text(db.unset(name))

    @app.get("/numequalto")
    def numequalto():
        try:
            value = param("value")
        except ValueError as error:
            logger.warning("Bad NUMEQUALTO request: %s", error)
            return text(f"ERROR: {error}", 400)
        return text(db.numequalto(value))

    @app.get("/undo")
    def undo():
        return text(db.undo())

    @app.get("/redo")
    def redo():
        return text(db.redo())

    @app.get("/end")
    def end():
        return text(db.end())

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
