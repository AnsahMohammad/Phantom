import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
from phantom.core.query_engine import Phantom_Query
from phantom.utils.parser import Parser
from supabase import create_client, Client
import requests
import json

# setting up database
REMOTE_DB = True
tracking = os.environ.get("TRACKING", "1") == "1"
url: str = os.environ.get("SUPABASE_URL", None)
key: str = os.environ.get("SUPABASE_KEY", None)

beta_AI = os.environ.get("BETA", "1") == "1"

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    print(f"Error while creating Supabase client: {e}")
    REMOTE_DB = False
else:
    print("Connected to Supabase")

# setting up the query engine
app = Flask(__name__)
engine = Phantom_Query("indexed", title_path="titles.json")
parser = Parser()


@app.route("/", methods=["GET"])
def home():
    input_text = request.args.get("q", "")
    print("recieved request : ", request.args)
    result = ["www.google.com", 0, "Google"]
    if input_text:
        result = process_input(input_text)
        return render_template("result.html", result=result, input_text=input_text)
    return render_template("home.html", result=result)

def analytics():
    if not REMOTE_DB or not tracking:
        return False
    input_text = request.args.get("q", "")
    browser = request.args.get("browser", "")
    device = request.args.get("device", "")
    try:
        data, count = (
            supabase.table("queries")
            .insert({"query": input_text, "browser": browser, "device": device})
            .execute()
        )
    except Exception as e:
        print(f"\nError inserting record into 'queries' table: {e}\n")
        return False
    return True

def process_input(input_text):
    result = engine.query(input_text, count=20)
    analytics()
    return result


@app.route("/ai_process", methods=["POST"])
def ai_process():
    if not beta_AI:
        return jsonify(generated_text=None), 500

    input_text = request.json.get("input_text", "")
    data = json.dumps({"inputs": input_text})
    models = "https://api-inference.huggingface.co/models/google/flan-t5-small", "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-128k-instruct"
    token = os.environ.get("AI_TOKEN", None)
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    generated_text = None
    try:
        response = requests.request(
            "POST", models[0], headers=headers, data=data, timeout=10
        )
        response_json = json.loads(response.content.decode("utf-8"))[0]
        generated_text = response_json.get('generated_text', None)
        print("AI response: ", json.dumps(response_json, indent=4))

    except Exception as e:
        print(f"Error while sending request to AI model: {e}")
        return jsonify(generated_text=None), 500

    return jsonify(generated_text=generated_text), 200

@app.route("/health", methods=["GET"])
def health_check():
    return "OK", 200


if __name__ == "__main__":
    app.run()
