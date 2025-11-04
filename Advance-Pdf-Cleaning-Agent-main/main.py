from flask import Flask, request, jsonify, send_file
import pdfplumber
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from xhtml2pdf import pisa  # For HTML-to-PDF conversion
import os
import tempfile
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configure Gemini AI
genai.configure(api_key="AIzaSyA2TOZ3aO3XVO5ge84UIHV0vp3WETmui2E")  # Replace with your API key
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF while preserving structure"""
    extracted_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                extracted_text.append(text)
    return "\n\n".join(extracted_text)

def clean_text_with_gemini(text, removal_prompt):
    """Clean text using Gemini AI and return HTML"""
    prompt = f"""
    Here is a document extracted from a PDF:

    {text}

    Instructions: {removal_prompt}

    Return **only the cleaned content** in **HTML format** with:
    - Headings (`<h1>`, `<h2>`)
    - Paragraphs (`<p>`)
    - Lists (`<ul>`, `<ol>`, `<li>`)
    - Tables (`<table>`, `<tr>`, `<td>`)
    - Bold/Italic (`<strong>`, `<em>`)
    - Line breaks (`<br>`)

    Do NOT include `<html>`, `<head>`, or `<body>` tags. Just the content.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def save_cleaned_html_to_pdf(html_content, output_path):
    """Convert HTML to PDF using xhtml2pdf"""
    with open(output_path, "wb") as pdf_file:
        pisa.CreatePDF(
            html_content,
            dest=pdf_file,
            encoding='utf-8'
        )

@app.route('/clean-pdf', methods=['POST'])
def clean_pdf():
    """API endpoint to process PDF cleaning"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        if 'prompt' not in request.form:
            return jsonify({"error": "No cleaning prompt provided"}), 400

        pdf_file = request.files['file']
        removal_prompt = request.form['prompt']

        if not pdf_file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        # Create temporary files
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, f"input_{uuid.uuid4()}.pdf")
        output_path = os.path.join(temp_dir, f"cleaned_{uuid.uuid4()}.pdf")

        pdf_file.save(input_path)

        # Process the PDF
        extracted_text = extract_text_from_pdf(input_path)
        cleaned_html = clean_text_with_gemini(extracted_text, removal_prompt)
        save_cleaned_html_to_pdf(cleaned_html, output_path)

        return send_file(
            output_path,
            as_attachment=True,
            download_name="cleaned_document.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return """
    <h1>PDF Cleaning Agent</h1>
    <p>Send a POST request to /clean-pdf with:</p>
    <ul>
        <li>PDF file (form field 'file')</li>
        <li>Cleaning instructions (form field 'prompt')</li>
    </ul>
    """

if __name__ == '__main__':
    app.run(debug=True)