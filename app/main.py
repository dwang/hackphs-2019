from flask import Flask, render_template, request

import json
import database

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/event", methods=["POST"])
def event():
    data = request.get_json(force=True)
    database.add_event(
        data["time"],
        data["x_position"],
        data["y_position"],
        data["baseline_y_position"],
        data["score"],
    )
    return "200"


@app.route("/events")
def events():
    return str(database.get_events())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
