# run the phantom flask app

python3 -m venv .env
source .env/bin/activate

pip install -r requirements.txt
python3 -m nltk.downloader stopwords
python3 -m nltk.downloader punkt

echo "running the server"

# python3 phantom.py
gunicorn -w 1 server:app
