python3 -m venv .env
source .env/bin/activate

pip install -r requirements.txt
python3 -m src.phantom --num_threads 10 --urls "https://www.geeksforgeeks.org/" "https://stackoverflow.com/questions" --show_logs True --print_logs True --sleep 60
