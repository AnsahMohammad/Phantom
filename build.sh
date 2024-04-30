source .env/bin/activate

pip install -r requirements.txt
clear
echo "Installation done"
python3 -m src.phantom_indexing
echo "Phantom Processing done"
clear
python3 -m src.query_engine
