# run the phantom flask app

python3 -m venv .env
source .env/bin/activate

pip install -r requirements.txt


export IDF_CONTENT=0
export IDF_TITLE=1
export CHUNK_SIZE=500
export CHUNK_LIMIT=2000


# python3 phantom.py
gunicorn -w 1 server:app
