python3 -m venv .env
source .env/bin/activate


pip install -r requirements.txt

# Check if SUPABASE_URL and SUPABASE_KEY are set
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    python3 -m src.phantom --num_threads 10 --urls "https://www.geeksforgeeks.org/" "https://en.wikipedia.org/wiki/India" "https://developers.cloudflare.com/" "https://bloggingidol.com/best-programming-blogs/" "https://www.hindustantimes.com/india-news/" "https://www.bbc.com/news" --show_logs True --print_logs True --sleep 240
fi

clear
echo "Installation done"
python3 -m nltk.downloader stopwords
python3 -m nltk.downloader punkt
ls
python3 -m src.phantom_indexing
echo "Phantom Processing done"
clear
echo "Build done"
