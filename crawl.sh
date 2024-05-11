# crawler script to crawl the given urls
# background crawler to update the indexer for realtime data
# background crawler to update the indexer for realtime data

python3 -m venv .env
source .env/bin/activate

pip install -r requirements.txt
python3 -m phantom.main --num_threads 3 --urls "https://www.aljazeera.com/" "https://www.bbc.com/news" "https://www.ndtv.com/" --show_logs True --sleep 120
