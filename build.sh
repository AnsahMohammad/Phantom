source .env/bin/activate

cd Phantom
pip install -r requirements.txt
clear
echo "Installation done"
python3 phantom_indexing.py
echo "Phantom Processing done"
clear
python3 query_engine.py
