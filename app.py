import os
import hashlib

import requests
import yaml
from urllib.parse import urlparse
from flask import Flask, request, jsonify


app = Flask(__name__)


# Allowed external domains for /fetch endpoint
ALLOWED_HOSTS = [
    "api.github.com"
]


def is_allowed_url(url):
    parsed = urlparse(url)

    return (
        parsed.scheme in ["http", "https"]
        and parsed.hostname in ALLOWED_HOSTS
    )


STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")


LEDGER = [
    {
        "id": "txn_1001",
        "pan": "4242424242424242",
        "amount": 4200,
        "currency": "USD",
        "status": "captured"
    },
    {
        "id": "txn_1002",
        "pan": "5555555555554444",
        "amount": 1899,
        "currency": "EUR",
        "status": "refunded"
    },
]


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/tokenize", methods=["POST"])
def tokenize():

    payload = request.get_json(silent=True) or {}

    pan = payload.get("pan", "")

    token = "tok_" + hashlib.sha256(
        pan.encode()
    ).hexdigest()[:24]

    return jsonify(
        token=token,
        last4=pan[-4:]
    )


@app.route("/transactions")
def transactions():

    return jsonify(
        transactions=LEDGER
    )


@app.route("/import", methods=["POST"])
def import_config():

    # Secure YAML parsing
    config = yaml.safe_load(request.data)

    return jsonify(
        loaded=str(config)
    )


@app.route("/fetch")
def fetch():

    url = request.args.get("url", "")

    # Prevent SSRF attacks
    if not is_allowed_url(url):
        return jsonify(
            error="URL not allowed"
        ), 400


    resp = requests.get(
        url,
        timeout=5
    )

    return jsonify(
        status_code=resp.status_code,
        body=resp.text[:2048]
    )


if __name__ == "__main__":

    # Required for Kubernetes container networking
    app.run(
        host="0.0.0.0",
        port=8080
    )
