# index the documents and run the query engine

source .env/bin/activate

pip install -r requirements.txt
clear
echo "Installation done"
sleep 2
# clear
python3 -m phantom.core.query_engine
