python3 -m venv .env
source .env/bin/activate

cd Phantom
pip install -r requirements.txt
python phantom.py --num_threads 8 --urls "https://www.geeksforgeeks.org/" "https://stackoverflow.com/questions" --show_logs True --print_logs True --sleep 900
