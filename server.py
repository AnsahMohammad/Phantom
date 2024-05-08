import os
from flask import Flask, render_template, request, redirect, url_for
from phantom.core.query_engine import Phantom_Query
from phantom.utils.parser import Parser
from supabase import create_client, Client

# setting up database
REMOTE_DB = True
url: str = os.environ.get("SUPABASE_URL", None)
key: str = os.environ.get("SUPABASE_KEY", None)
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
    if input_text:
        result = process_input(input_text)
        return render_template("result.html", result=result, input_text=input_text)
    return render_template("home.html")


def analytics(input_text):
    if not REMOTE_DB:
        return False
    try:
        data, count = supabase.table("queries").insert({"query": input_text}).execute()
    except Exception as e:
        print(f"\nError inserting record into 'queries' table: {e}\n")
        return False
    return True


def process_input(input_text):
    result = engine.query(input_text, count=20)  # (doc, score, title)
    analytics(input_text)
    return result


@app.route("/health", methods=["GET"])
def health_check():
    return "OK", 200


if __name__ == "__main__":
    app.run()
