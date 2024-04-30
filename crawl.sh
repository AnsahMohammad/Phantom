python3 -m venv .env
source .env/bin/activate

cd phantom_crawler
pip install -r requirements.txt
python3 phantom_engine.py
