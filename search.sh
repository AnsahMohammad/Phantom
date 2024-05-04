# run the phantom flask app

python3 -m venv .env
source .env/bin/activate

pip install -r requirements.txt
# python3 phantom.py
gunicorn -w 4 phantom:app
