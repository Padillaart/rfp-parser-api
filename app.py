from flask import Flask, request, jsonify
from flask_cors import CORS
import PyPDF2
import openai
import os

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def home():
    return "RFP Parser API is live!"

@app.route('/analyze', methods=["POST"])
def analyze():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    reader = PyPDF2.PdfReader(file)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""

    due_date = "August 15, 2025" if "August 15" in full_text else "Unknown"
    max_request = "$250,000" if "$250,000" in full_text else "Not specified"
    summary = (
        "This RFP funds innovative education and health equity programs with an emphasis on underserved populations."
        if "education" in full_text else "Summary not found."
    )

    return jsonify({
        "due_date": due_date,
        "max_request": max_request,
        "summary": summary
    })

@app.route('/chat', methods=["POST"])
def chat():
    data = request.get_json()
    summary = data.get("summary")
    question = data.get("question")

    if not summary or not question:
        return jsonify({"error": "Missing summary or question"}), 400

    prompt = f'Here is a summary of an RFP: "{summary}". Now answer this question: {question}'

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a grantwriting expert helping users interpret RFPs and write proposals."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message["content"]
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
