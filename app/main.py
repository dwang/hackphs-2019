from flask import Flask, render_template, request
from bson.json_util import dumps
from flask_cors import CORS

import json
import database

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/event", methods=["POST"])
def event():
    data = request.get_json(force=True)
    database.add_event(
        data["time"],
        data["score"],
    )
    return "200"

previous = "False"

@app.route("/calibrate", methods=["GET", "POST"])
def calibrate():
    global previous

    output = previous

    if request.method == "POST":
        previous = "True"
    else:
        previous = "False"

    return output

output = "False"

@app.route("/blur", methods=["GET", "POST"])
def blur():
    global output

    if request.method == "POST":
        output = request.get_data()

    return output


@app.route("/events")
def events():
    return dumps(database.get_events())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
