import re
import random
import json

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load brand data
with open("brands_data.json", "r") as f:
    brand_data = json.load(f)

# Brand aliases
brand_alias = {
    "MK": "Michael Kors",
    "NK": "Nike",
    "AD": "Adidas",
    "LV": "Louis Vuitton",
    "GC": "Gucci",
    "PR": "Prada",
    "BB": "Burberry",
    "FD": "Fendi",
    "RX": "Rolex",
    "CH": "Coach"
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    brand = data.get("brand")
    model = data.get("model")
    price = data.get("price")
    serial = data.get("serial")

    # Required fields validation
    if not brand or not model or not price:
        return jsonify({
            "error": "Please fill all required fields"
        })

    # Convert short brand names
    if brand in brand_alias:
        brand = brand_alias[brand]

    # Unknown brand handling
    if brand not in brand_data:
        return jsonify({
            "classification": "Unknown",
            "message": "Brand not available in database",
            "suggestion": "Please contact support or add brand data."
        })

    brand_info = brand_data[brand]

    original_price = brand_info["avg_price"]
    valid_models = brand_info["models"]
    serial_prefix = brand_info["serial_prefix"]

    score = 0
    reasons = []

    # Brand exists
    score += 10
    reasons.append("Brand supported")

    # Price logic
    ratio = price / original_price

    if ratio > 0.8:
        score += 40
        reasons.append("Price close to original")

    elif ratio > 0.5:
        score += 25
        reasons.append("Price slightly lower")

    elif ratio > 0.3:
        score += 10
        reasons.append("Price moderately low")

    else:
        score += 5
        reasons.append("Price very low")

    # Suspiciously expensive
    if price > original_price * 1.5:
        reasons.append("Price unusually high")

    # Model validation
    if model in valid_models:
        score += 30
        reasons.append("Valid model")
    else:
        reasons.append("Invalid model")

    # Serial validation
    if serial and re.match(rf"^{serial_prefix}[0-9]{{5}}$", serial):
        score += 30
        reasons.append("Valid serial format")
    else:
        reasons.append("Invalid serial format")

    # Classification
    if score >= 90:
        classification = "Original"

    elif score >= 70:
        classification = "First Copy"

    elif score >= 50:
        classification = "Second Copy"

    else:
        classification = "Third Copy"

    # Realistic confidence
    confidence_value = max(
        0,
        min(score, 95) - random.randint(0, 5)
    )

    return jsonify({
        "brand": brand,
        "model": model,
        "serial": serial,
        "input_price": price,
        "expected_price": original_price,
        "score": score,
        "confidence": f"{confidence_value}%",
        "classification": classification,
        "reasons": reasons
    })


if __name__ == "__main__":
    app.run(debug=True)