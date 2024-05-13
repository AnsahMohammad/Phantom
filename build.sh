# build script for crawling and indexing

python3 -m venv .env
source .env/bin/activate

pip install -r requirements.txt

# Check if SUPABASE_URL and SUPABASE_KEY are set
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    sleep 1
    echo "SUPABASE_URL and SUPABASE_KEY are not set. Crawling..."
    # Use the first argument as the sleep duration, or 240 if no argument is passed
    sleep_duration=${1:-240}
    python3 -m phantom.main --num_threads 5 --urls "https://www.geeksforgeeks.org/" "https://en.wikipedia.org/wiki/India" "https://developers.cloudflare.com/" "https://bloggingidol.com/best-programming-blogs/" "https://www.hindustantimes.com/india-news/" "https://www.bbc.com/news" --show_logs True --print_logs True --sleep $sleep_duration
else
    echo "SUPABASE_URL and SUPABASE_KEY are set. Not crawling."
fi

echo "crawling done"
# clear
echo "Installation done"
# python3 -m nltk.downloader stopwords
# python3 -m nltk.downloader punkt
ls
python3 -m phantom.core.indexer
echo "Phantom Processing done"
# clear
echo "Build done"
