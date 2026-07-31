"""
Flask API for the ACA plan matcher.

POST /match
Body (JSON): { "zip_code": "27601", "age": "30", "income": 35000, "household_size": 1 }
Returns: full match_engine result as JSON
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from match_engine import get_plan_match
from explain import explain_plans

app = Flask(__name__)
CORS(app)  # allows requests from other origins, e.g. your React dev server

# Load data once at startup, not on every request
plans_df = pd.read_csv("clean-insurance-NC.csv")
zip_county_df = pd.read_csv("zip-county-NC.csv")


@app.route("/match", methods=["POST"])
def match():
    data = request.get_json()

    required_fields = ["zip_code", "age", "income", "household_size"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    try:
        result = get_plan_match(
            zip_code=str(data["zip_code"]),
            age=str(data["age"]),
            income=float(data["income"]),
            household_size=int(data["household_size"]),
            zip_county_df=zip_county_df,
            plans_df=plans_df,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if "error" in result:
        return jsonify(result), 404

    # Only call the LLM if the frontend asks for it -- keeps /match fast and
    # free by default, and explanation is an opt-in extra step.
    if data.get("explain"):
        try:
            result["explanation"] = explain_plans(result)
        except Exception as e:
            # If the LLM call fails, still return the plan data --
            # don't let an explanation failure break the whole match.
            result["explanation"] = None
            result["explanation_error"] = str(e)

    return jsonify(result)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "plans_loaded": len(plans_df)})


if __name__ == "__main__":
    app.run(debug=False, port=5050)
