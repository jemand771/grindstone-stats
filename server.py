import json
import os

from flask import Flask, render_template, request
import redis

import model
import security


app = Flask(__name__)
REDIS = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ.get("REDIS_PORT", "6379")),
    db=0,
    decode_responses=True
)

@app.post("/ingest")
def accept():
    token = security.verify_token(request.args.get("token"))
    data = json.loads(request.data.decode("utf-8"))
    db = model.GrindstoneDatabase.from_grindstone(data)
    encoded = db.to_grindstone()
    db2 = model.GrindstoneDatabase.from_grindstone(encoded)
    # TODO this probably needs error handling to send 400
    if db != db2:
        return "yeah idk the parser fucked up", 500
    REDIS.set(f"{token}.grindstone", json.dumps(encoded, indent=2, ensure_ascii=False))
    return "", 204


@app.get("/")
def main_page():
    token = security.verify_token(request.args.get("token"))
    data = json.loads(REDIS.get(f"{token}.grindstone"))
    db = model.GrindstoneDatabase.from_grindstone(data)
    analytics = model.Analytics(db)
    return render_template("index.html", analytics=analytics)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
