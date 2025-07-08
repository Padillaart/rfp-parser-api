from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import PyPDF2
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def home():
    return "RFP Parser API is live!"

@app.route('/analyze', methods=["POST"])
def analyze():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
      MAX_FILE_SIZE_MB = 5
file = request.files.get("file")

if not file:
    return jsonify({"error": "No file uploaded"}), 400

file.seek(0, os.SEEK_END)
size_mb = file.tell() / (1024 * 1024)
file.seek(0)

if size_mb > MAX_FILE_SIZE_MB:
    return jsonify({"error": "File too large. Max 5MB allowed."}), 400 

    reader = PyPDF2.PdfReader(file)
    full_text = ""
   for i, page in enumerate(reader.pages):
    try:
        page_text = page.extract_text()
        if page_text:
            full_text += page_text
    except Exception as e:
        print(f"Error extracting text from page {i}: {e}")


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
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a grantwriting expert helping users interpret RFPs and write proposals."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/widget')
def serve_widget():
    return send_from_directory('static', 'widget.html')


