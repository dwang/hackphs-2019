import pymongo
import json
import os

ip = os.getenv("MONGO_IP", "127.0.0.1")

client = pymongo.MongoClient(ip, 27017)
db = client["database"]
collection = db.collection


def add_event(time, x_position, y_position, baseline_y_position, score):
    post = {
        "time": time,
        "x_position": x_position,
        "y_position": y_position,
        "baseline_y_position": baseline_y_position,
        "score": score,
    }

    collection.insert_one(post)


def get_events():
    events = []

    for post in db.collection.find():
        events.append(post)

    return events
