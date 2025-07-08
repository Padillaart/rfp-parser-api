from flask import Flask, request, jsonify
import PyPDF2
import io

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    reader = PyPDF2.PdfReader(file)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""

    # Simulated parsing (replace with actual parsing logic)
    due_date = "August 15, 2025" if "August 15" in full_text else "Unknown"
    max_request = "$250,000" if "$250,000" in full_text else "Not specified"
    summary = "This RFP funds innovative education and health equity programs with an emphasis on underserved populations." if "education" in full_text else "Summary not found."

    return jsonify({
        "due_date": due_date,
        "max_request": max_request,
        "summary": summary
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)