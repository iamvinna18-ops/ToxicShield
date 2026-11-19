from spam_detector import detect_spam
from toxicity_detector import detect_toxicity
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "success",
        "message": "ToxicShield backend is running!"
    })

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    comments = data.get("comments", [])

    if not isinstance(comments, list) or not comments:
        return jsonify({"error": "Please provide comments"}), 400

    if not all(isinstance(c, str) for c in comments):
        return jsonify({"error": "Comments must be text"}), 400

    comments = [c.strip() for c in comments if c.strip()]

    return jsonify({
        "status": "success",
        "total_comments": len(comments),
        "message": "Comments received successfully!"
    })

@app.route("/api/upload-csv", methods=["POST"])
def upload_csv():
    if "file" not in request.files:
        return jsonify({"error": "No CSV uploaded"}), 400

    try:
        df = pd.read_csv(request.files["file"])

        if "comment" not in df.columns:
            return jsonify({
                "error": "CSV needs a comment column"
            }), 400

        comments = df["comment"].dropna().astype(str).tolist()

        return jsonify({
            "status": "success",
            "total_comments": len(comments),
            "comments": comments
        })

    except Exception:
        return jsonify({"error": "Invalid CSV file"}), 400
    
@app.route("/api/toxicity-check", methods=["POST"])
def toxicity_check():

    data = request.get_json()

    if not data or "comment" not in data:
        return jsonify({
            "error": "Please provide a comment"
        }), 400

    comment = data["comment"]

    if not isinstance(comment, str) or not comment.strip():
        return jsonify({
            "error": "Comment cannot be empty"
        }), 400

    result = detect_toxicity(comment)
    spam_result = detect_spam(comment)
    return jsonify({
        "comment": comment,

        # Toxicity detection
        "category": result["category"],
        "confidence": result["confidence"],

        # Spam detection
        "spam": spam_result["is_spam"],
        "spam_risk_score": spam_result["risk_score"],
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
