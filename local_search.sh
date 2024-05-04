# index the documents and run the query engine

source .env/bin/activate

pip install -r requirements.txt
clear
echo "Installation done"
python3 -m src.phantom_indexing
echo "Phantom Indexing done"
clear
python3 -m src.query_engine
