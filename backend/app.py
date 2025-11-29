from flask import Flask, request, jsonify
from flask_cors import CORS
import redis
import uuid
from Crypto.Cipher import AES
import base64
import os
import time
import hashlib

app = Flask(__name__)
CORS(app)

r = redis.Redis(host="redis", port=6379, db=0)

SECRET_KEY = b"THIS_IS_32_BYTE_KEY_FOR_AES_256!!"

def encrypt(text):
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(text.encode())
    return base64.b64encode(cipher.nonce + ciphertext).decode()

def decrypt(ciphertext):
    raw = base64.b64decode(ciphertext)
    nonce = raw[:16]
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX, nonce)
    decrypted = cipher.decrypt(raw[16:])
    return decrypted.decode()

@app.route("/create", methods=["POST"])
def create_secret():
    data = request.json
    secret = data.get("secret")
    password = data.get("password")
    expiry = int(data.get("expiry", 3600))

    key = str(uuid.uuid4())

    payload = {
        "secret": encrypt(secret),
        "password": hashlib.sha256(password.encode()).hexdigest() if password else "",
        "expiry": int(time.time()) + expiry
    }

    r.set(key, str(payload))
    return jsonify({"url": f"/retrieve/{key}"})


@app.route("/retrieve/<key>", methods=["POST"])
def retrieve_secret(key):
    stored = r.get(key)
    if not stored:
        return jsonify({"error": "Secret expired or invalid"}), 404

    stored = eval(stored.decode())
    password = request.json.get("password")

    if stored["password"]:
        if hashlib.sha256(password.encode()).hexdigest() != stored["password"]:
            return jsonify({"error": "Invalid password"}), 403

    if time.time() > stored["expiry"]:
        r.delete(key)
        return jsonify({"error": "Secret expired"}), 410

    secret = decrypt(stored["secret"])
    r.delete(key)

    return jsonify({"secret": secret})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

