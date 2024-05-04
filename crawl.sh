# crawler script to crawl the given urls

python3 -m venv .env
source .env/bin/activate

pip install -r requirements.txt
python3 -m src.phantom --num_threads 10 --urls "https://www.geeksforgeeks.org/" "https://en.wikipedia.org/wiki/India" "https://developers.cloudflare.com/" "https://bloggingidol.com/best-programming-blogs/" "https://www.hindustantimes.com/india-news/" "https://www.bbc.com/news" --show_logs True --print_logs True --sleep 1800
