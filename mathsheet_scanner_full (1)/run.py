# run.py
from flask import Flask, request, jsonify, render_template
import base64

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/scan", methods=["POST"])
def scan():
    try:
        data = request.get_json()

        if "image" not in data:
            return jsonify({"success": False, "error": "No image provided"}), 400

        image_base64 = data["image"]

        # Decode image if needed
        if "," in image_base64:
            _, encoded = image_base64.split(",", 1)
            image_data = base64.b64decode(encoded)

        posted_problems = data.get("problems", [])
        processed = []

        for p in posted_problems:
            q = p.get("question", "").strip()
            ua = p.get("userAnswer", "").strip()

            try:
                # Very basic math evaluation (safe for simple arithmetic only)
                correct = str(eval(q.replace("=", "").strip()))
            except Exception:
                correct = "?"

            processed.append({
                "question": q,
                "userAnswer": ua,
                "correctAnswer": correct,
                "isCorrect": ua == correct
            })

        return jsonify({"success": True, "problems": processed})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
