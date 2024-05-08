import json
from collections import Counter
from ..utils.logger import Logger
import os
from supabase import create_client, Client

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import string


class Phantom_Query:
    def __init__(self, filename="indexed", title_path=None):

        self.showlogs = True
        self.title_table = False
        self.remote_db = self.check_remote()
        self.logger = Logger(self.showlogs)
        self.log = self.logger.log

        self.CONTENT_WEIGHT = 1
        self.TITLE_WEIGHT = 3

        self.load(filename)

        if title_path or self.remote_db:
            self.title_path = title_path
            self.title_table = True
            self.titles = {}
            if not self.load_titles():
                self.remote_db = False
                self.load_titles()

        # self.tf = self.data["tf"]
        self.idf = self.data["idf"]
        self.tfidf = self.data["tfidf"]

        self.t_idf = self.t_data["idf"]
        self.t_tfidf = self.t_data["tfidf"]

        self.lookup = set(self.idf.keys())
        self.t_lookup = set(self.t_idf.keys())
        self.log("Query Engine Ready", "Query_Engine")
    
    def load(self, filename):
        self.data = {}
        with open(filename+".json", "r") as f:
            self.data = json.load(f)
        
        self.t_data = {}
        with open("title_" + filename + ".json", "r") as f:
            self.t_data = json.load(f)

    def query(self, query, count=10):
        self.log(f"Query received : {query}", "Query_Engine")

        # Process the query
        stemmer = PorterStemmer()
        stop_words = set(stopwords.words("english"))
        processed_query = []
        try:
            words = word_tokenize(query)
            for word in words:
                word = word.lower().translate(str.maketrans("", "", string.punctuation))
                if word not in stop_words and len(word) < 30:
                    stemmed_word = stemmer.stem(word)
                    processed_query.append(stemmed_word)
        except Exception as e:
            self.log(f"Error processing query: {e}", "Query_Engine")

        query = processed_query
        query_len = len(query)


        query = [term for term in query if term in self.lookup]
        query_freq = Counter(query)
        query_tfidf = {
            term: (query_freq[term] / query_len) * self.idf.get(term,0.0) for term in query
        }

        query = processed_query
        query = [term for term in query if term in self.t_lookup]
        query_freq = Counter(query)
        query_t_tfidf = {
            term: (query_freq[term] / query_len) * self.t_idf.get(term, 0.0) for term in query
        }

        self.log(f"TF-idf of query : {query_tfidf}", "Query_Engine")

        scores = {}
        for doc, tfidf in self.tfidf.items():
            score = sum(tfidf[term] * query_tfidf.get(term, 0.0) for term in tfidf)
            scores[doc] = self.CONTENT_WEIGHT * score

        for doc, tfidf in self.t_tfidf.items():
            score = sum(tfidf[term] * query_t_tfidf.get(term, 0.0) for term in tfidf)
            scores[doc] += self.TITLE_WEIGHT * score

        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        self.log(f"Ranked documents : {ranked_docs[:count]}", "Query_Engine")

        final_results = []
        for doc, score in ranked_docs[:count]:
            title = self.titles[doc] if self.title_table else None
            final_results.append((doc, score, title))

        return final_results

    def run(self):
        while True:
            query = input("Enter the query : ")
            print(self.query(query))

    def check_remote(self):
        remote_db = True

        self.db_url = os.environ.get("SUPABASE_URL", None)
        self.db_key = os.environ.get("SUPABASE_KEY", None)
        try:
            self.supabase = create_client(self.db_url, self.db_key)
            if not self.supabase:
                print("Failed to connect to Supabase")
                remote_db = False
        except Exception as e:
            print(f"Error while creating Supabase client: {e}")
            remote_db = False

        print("Remote database : ", remote_db)
        print("DB Ready")
        return remote_db

    def load_titles(self):
        # load the titles from index.json
        if self.remote_db:
            try:
                self.log("Fetching data from remote DB")
                start = 0
                end = 999
                while True:
                    response = (
                        self.supabase.table("index")
                        .select("url", "title")
                        .range(start, end)
                        .execute()
                    )
                    if not response.data:
                        break
                    for record in response.data:
                        self.titles[record["url"]] = record["title"]
                    start += 1000
                    end += 1000
                    self.log(
                        f"Data fetched from remote DB: {len(self.titles)}",
                        "Phantom-Indexer-Loader",
                    )
                self.log(
                    f"Data fetched from remote DB: {len(self.titles)}",
                    "Phantom-Indexer-Loader",
                )
            except Exception as e:
                print(f"\nError fetching data from index table: {e}\n")
                return False
            return True

        else:
            if not self.title_path:
                return False

            self.log("Loading data from local file")
            with open(self.title_path, "r") as f:
                self.titles = json.load(f)


if __name__ == "__main__":
    query_engine = Phantom_Query("indexed")
    query_engine.run()
