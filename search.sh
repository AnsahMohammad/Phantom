# run the phantom flask app

python3 -m venv .env
source .env/bin/activate

pip install -r requirements.txt

echo "running the server"

gunicorn -w 1 server:app
