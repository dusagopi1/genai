from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# API URL (Update with your live URL)
API_URL = "https://a796-34-169-214-95.ngrok-free.app/generate"

@app.route("/", methods=["GET", "POST"])
def index():
    response_text = ""
    
    if request.method == "POST":
        prompt = request.form.get("prompt")  # Get user input from form
        if prompt:
            data = {"prompt": prompt}
            response = requests.post(API_URL, json=data)  # Send request to API
            response_text = response.json().get("response", "No response received")

    return render_template("index.html", response=response_text)

if __name__ == "__main__":
    pass
