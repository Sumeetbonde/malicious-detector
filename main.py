from flask import Flask, render_template, request
import google.generativeai as genai
import os
import PyPDF2

app = Flask(__name__)

# Configure Gemini
os.environ["GOOGLE_API_KEY"] = "AIzaSyDf6c21od5rrPOd1ASpXZ5O9qpwM5GzZoA"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")


# Function 1: Email Scam Detection
def detect_scam_email_content(text):
    prompt = f"""You are an expert in identifying scam messages in emails, SMS, etc.
Analyze the text and classify it as:

- **Real/Legitimate**: Authentic, safe message
- **Scam/Fake**: Phishing, fraud, or suspicious message

Text:
{text}

Return a clear and concise message indicating whether this content is real or scam."""

    response = model.generate_content(prompt)
    return response.text.strip()


# Function 2: URL Classification
def url_detection(url):
    prompt = f"""You are an Advanced AI specializing in URL security classification. Analyze the following URL and classify it as one of:

1. Safe
2. Phishing
3. Malware
4. Defacement

Example:
- Safe: "https://www.google.com/"
- Phishing: "https://secure-login.paypal.com/"
- Defacement: "https://hacked-website.com/"
- Malware: "https://free-download-software.xyz/"

Input URL: {url}

Output:
- Return only the classification name."""

    response = model.generate_content(prompt)
    return response.text.strip() if response else "Detection failed"


# Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scam", methods=['GET', 'POST'])  # fixed 'method' to 'methods'
def detect_scam():
    if request.method == 'POST':
        if "file" not in request.files:
            return render_template("index.html", message="No file uploaded")

        file = request.files['file']
        extracted_text = ""

        if file.filename.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(file)
            extracted_text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

        elif file.filename.endswith('.txt'):
            extracted_text = file.read().decode("utf-8")
        else:
            return render_template("index.html", message="Unsupported file type. Please upload a .pdf or .txt file")

        message = detect_scam_email_content(extracted_text)
        return render_template("index.html", message=message)

    return render_template("index.html")


@app.route("/predict", methods=['GET', 'POST'])  # fixed 'method' to 'methods'
def url_predict():
    if request.method == 'POST':
        url = request.form.get("url", '').strip()
        if not url.startswith(('http://', 'https://')):
            return render_template("index.html", predicted_class="Invalid URL format")

        classification = url_detection(url)
        return render_template("index.html", input_url=url, predicted_class=classification)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
