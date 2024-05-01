python3 -m venv .env
source .env/bin/activate

pip install -r requirements.txt
python3 -m src.phantom --num_threads 10 --urls "https://www.geeksforgeeks.org/" "https://stackoverflow.com/questions" "https://en.wikipedia.org/wiki/India" "https://developers.cloudflare.com/" "https://bloggingidol.com/best-programming-blogs/" --show_logs True --print_logs True --sleep 600

clear
echo "Installation done"
python3 -m nltk.downloader stopwords
python3 -m nltk.downloader punkt
ls
python3 -m src.phantom_indexing
echo "Phantom Processing done"
clear
echo "Build done"
