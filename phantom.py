import os
from flask import Flask, render_template, request, redirect, url_for
from src.query_engine import Phantom_Query
from src.phantom_engine import Parser
from supabase import create_client, Client

# setting up database
REMOTE_DB = True
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
if not supabase:
    print("Failed to connect to Supabase")
    REMOTE_DB = False
print("Connected to Supabase")

# setting up the query engine
app = Flask(__name__)
engine = Phantom_Query("indexed.json", titles="titles.json")
parser = Parser()

@app.route("/", methods=["GET"])
def home():
    input_text = request.args.get('q', '')
    if input_text:
        result = process_input(input_text)
        return render_template("result.html", result=result, input_text=input_text)
    return render_template("home.html")

def analytics(input_text):
    if not REMOTE_DB:
        return False
    try:
        data, count = supabase.table('queries').insert({"query": input_text}).execute()
    except Exception as e:
        print(f"\nError inserting record into 'queries' table: {e}\n")
        return False
    return True

def process_input(input_text):
    result = engine.query(input_text, count=20)         # (doc, score, title)
    analytics(input_text)
    return result

@app.route("/health", methods=["GET"])
def health_check():
    return "OK", 200

if __name__ == "__main__":
    app.run()