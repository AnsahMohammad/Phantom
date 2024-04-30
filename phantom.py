from flask import Flask, render_template, request
from src.query_engine import Phantom_Query

app = Flask(__name__)
engine = Phantom_Query("src/indexed.json")

@app.route('/', methods=['GET', 'POST'])
def home():
    input_text = ""
    if request.method == 'POST':
        input_text = request.form.get('input_text')
        result = process_input(input_text)
        return render_template('result.html', result=result, input_text=input_text)
    return render_template('home.html', input_text=input_text)

def process_input(input_text):
    result = engine.query(input_text)
    return result[:20]

if __name__ == '__main__':
    app.run(debug=True)