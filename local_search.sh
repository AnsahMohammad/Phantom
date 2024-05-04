source .env/bin/activate

pip install -r requirements.txt
clear
echo "Installation done"
clear
python3 -m src.query_engine
