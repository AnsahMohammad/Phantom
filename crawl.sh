# crawler script to crawl the given urls

python3 -m venv .env
source .env/bin/activate

pip install -r requirements.txt
python3 -m phantom.main --num_threads 10 --urls "https://www.geeksforgeeks.org/" "https://en.wikipedia.org/wiki/India" "https://bloggingidol.com/best-programming-blogs/" "https://www.hindustantimes.com/india-news/" "https://www.bbc.com/news" "https://simple.wikipedia.org/wiki/List_of_fruits" "https://www.hsph.harvard.edu/nutritionsource/healthy-eating-plate/" "https://www.imdb.com/search/keyword/?keywords=anime" "https://pagesix.com/" "https://dph.illinois.gov/topics-services/diseases-and-conditions/diseases-a-z-list.html" --show_logs True --print_logs True --sleep 1800
