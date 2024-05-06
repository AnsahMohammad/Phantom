import json
from collections import Counter
from .utils.logger import Logger
import os
from supabase import create_client, Client



class Phantom_Query:
    def __init__(self, filename="indexed.json", title_path=None):

        self.showlogs = True
        self.title_table = False
        self.remote_db = self.check_remote()
        self.logger = Logger(self.showlogs)
        self.log = self.logger.log
        
        self.data = {}
        with open(filename, "r") as f:
            self.data = json.load(f)

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


        self.lookup = set(self.idf.keys())
        self.log("Query Engine Ready", "Query_Engine")

    def query(self, query, count=10):
        self.log(f"Query recieved : {query}", "Query_Engine")
        query = query.split()
        query_len = len(query)
        query = [term for term in query if term in self.lookup]
        query_freq = Counter(query)
        query_tfidf = {
            term: (query_freq[term] / query_len) * self.idf[term] for term in query
        }

        self.log(f"TF-idf of query : {query_tfidf}", "Query_Engine")

        scores = {}
        for doc, tfidf in self.tfidf.items():
            score = sum(tfidf[term] * query_tfidf.get(term, 0.0) for term in tfidf)
            scores[doc] = score

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
                response = self.supabase.table("index").select("url", "title").execute()
                for record in response.data:
                        self.titles[record["url"]] = record["title"]
                self.log(f"Data fetched from remote DB: {len(self.titles)}", "Phantom-Indexer-Loader")
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
    query_engine = Phantom_Query("indexed.json")
    query_engine.run()
