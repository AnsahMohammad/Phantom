python3 -m venv .env
source .env/bin/activate

pip install -r requirements.txt
python3 -m src.phantom --num_threads 10 --urls "https://www.geeksforgeeks.org/" "https://stackoverflow.com/questions" "https://en.wikipedia.org/wiki/India" "https://developers.cloudflare.com/" --show_logs True --print_logs True --sleep 600
