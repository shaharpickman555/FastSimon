import logging
import os

from flask import Flask, render_template, request


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.get("/")
def hello_world():
    logger.info("Serving Hello World", extra={"path": request.path})
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
