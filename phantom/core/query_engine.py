import json
from collections import Counter, defaultdict
from ..utils.logger import Logger
from ..utils.storage import Database
import os

import string


class Phantom_Query:
    def __init__(self, filename="indexed", title_path=None):

        self.showlogs = True
        self.title_table = False
        self.logger = Logger(self.showlogs)
        self.log = self.logger.log

        db = Database()
        self.remote_db = db.state

        self.IDF_CONTENT = os.environ.get("IDF_CONTENT", "1") == "1"
        self.IDF_TITLE = os.environ.get("IDF_TITLE", "1") == "1"
        self.CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 500))
        self.CHUNK_LIMIT = int(os.environ.get("CHUNK_LIMIT", 10000))

        self.log(
            f"Query Engine called for in: {filename}\n IDF_CONTENT: {self.IDF_CONTENT}\n IDF_TITLE: {self.IDF_TITLE}",
            "Query_Engine",
        )

        self.CONTENT_WEIGHT = int(os.environ.get("CONTENT_WEIGHT", 1))
        self.TITLE_WEIGHT = int(os.environ.get("TITLE_WEIGHT", 2))

        self.data = {}
        self.load(filename)

        if title_path or self.remote_db:
            self.title_path = title_path
            self.title_table = True
            self.titles = {}
            if not self.load_titles():
                self.log("Failed to load titles", "Query_Engine")
                self.title_table = False
            else:
                self.log("Titles loaded", "Query_Engine")

        self.log("Query Engine Ready", "Query_Engine")


    def load(self, filename):
        if self.IDF_CONTENT:
            with open(filename + ".json", "r") as f:
                loaded_data = json.load(f)
                self.data = loaded_data['data']
                self.idf = self.data["idf"]
                self.tfidf = self.data["tfidf"]
            self.lookup = set(self.idf.keys())

        if self.IDF_TITLE:
            self.t_data = {}
            with open("title_" + filename + ".json", "r") as f:
                loaded_data = json.load(f)
                self.t_data = loaded_data['data']
            self.t_idf = self.t_data["idf"]
            self.t_tfidf = self.t_data["tfidf"]
            self.t_lookup = set(self.t_idf.keys())

    def query(self, query, count=10):
        self.log(f"Query received : {query}", "Query_Engine")

        # Process the query

        processed_query = []
        try:
            words = query.split()
            for word in words:
                word = word.lower().translate(str.maketrans("", "", string.punctuation))
                processed_query.append(word)

        except Exception as e:
            self.logger.error(f"Error processing query: {e}", "Query_Engine-query")

        query = processed_query
        query_len = len(query)

        scores = defaultdict(float)

        if self.IDF_CONTENT:
            query = [term for term in query if term in self.lookup]
            query_freq = Counter(query)
            query_tfidf = {
                term: (query_freq[term] / query_len) * self.idf.get(term, 0.0)
                for term in query
            }
            self.log(f"Title TF-idf of query : {query_tfidf}", "Query_Engine")

            for doc, tfidf in self.tfidf.items():
                score = sum(tfidf[term] * query_tfidf.get(term, 0.0) for term in tfidf)
                scores[doc] = self.CONTENT_WEIGHT * score

        if self.IDF_TITLE:
            query = processed_query
            query = [term for term in query if term in self.t_lookup]
            query_freq = Counter(query)
            query_t_tfidf = {
                term: (query_freq[term] / query_len) * self.t_idf.get(term, 0.0)
                for term in query
            }
            self.log(f"TF-idf of query : {query_t_tfidf}", "Query_Engine")

            for doc, tfidf in self.t_tfidf.items():
                score = sum(
                    tfidf[term] * query_t_tfidf.get(term, 0.0) for term in tfidf
                )
                scores[doc] += self.TITLE_WEIGHT * score

        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        self.log(f"Ranked documents : {ranked_docs[:count]}", "Query_Engine")

        final_results = []
        for doc, score in ranked_docs[:count]:
            try:
                title = self.titles[doc] if self.title_table else doc
                final_results.append((doc, score, title))
            except Exception as e:
                self.logger.error(
                    f"Error processing document {doc}: {e}", "Query_Engine-query"
                )
                continue
        return final_results

    def run(self):
        while True:
            query = input("Enter the query : ")
            print(self.query(query))

    def load_titles(self):
        # load the titles from index.json
        if self.title_table:
            self.log("Loading data from local file")
            with open(self.title_path, "r") as f:
                self.titles = json.load(f)
            self.log(f"Data loaded from local file: {len(self.titles)}")
            return True

        elif self.remote_db:
            try:
                self.log("Fetching data from remote DB")
                start = 0
                end = self.CHUNK_SIZE - 1
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
                    start += self.CHUNK_SIZE
                    end += self.CHUNK_SIZE
                    self.log(
                        f"Data fetched from remote DB: {len(self.titles)}",
                        "Phantom-Indexer-Loader",
                    )

                    if len(self.titles) > self.CHUNK_LIMIT:
                        self.log("CHUNK limit reached", "Phantom-Indexer-Loader")
                        break

                self.log(
                    f"Data fetched from remote DB: {len(self.titles)}",
                    "Phantom-Indexer-Loader",
                )
            except Exception as e:
                self.logger.error(
                    f"Error fetching data from index table: {e}",
                    "Phantom-Indexer-Loader",
                )
                return False
            return True

        else:
            if not self.title_path:
                return False


if __name__ == "__main__":
    query_engine = Phantom_Query("indexed", title_path="titles.json")
    query_engine.run()
