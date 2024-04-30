# Phantom Search
Light weight python based search engine

## Set-up
1) open `crawl.sh` and update the parameters

```shell
python phantom.py --num_threads 8 --urls "site1.com" "site2.com"
```
2) now run crawl.sh by typing 
```shell
./crawl.sh
```
This crawls the web and saves indices into `index.json` file

3) run `build.sh` to Process the indices and run the `Query Engine`

4) now everytime you can start the query engine by running the file `query_engine.py`


