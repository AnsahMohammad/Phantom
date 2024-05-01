import json
from collections import Counter
from .logger import Logger


class Phantom_Query:
    def __init__(self, filename="src/indexed.json", titles = None):

        self.showlogs = True
        self.title_table = False

        self.data = {}
        with open(filename, "r") as f:
            self.data = json.load(f)

        if titles:
            self.title_table = True
            self.titles = {}
            with open(titles, "r") as f:
                self.titles = json.load(f)

        # self.tf = self.data["tf"]
        self.idf = self.data["idf"]
        self.tfidf = self.data["tfidf"]

        self.logger = Logger(self.showlogs)
        self.log = self.logger.log

        self.lookup = set(self.idf.keys())
        self.log("Query Engine Ready", "Query_Engine")

    def query(self, query, count = 10):
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


if __name__ == "__main__":
    query_engine = Phantom_Query("src/indexed.json")
    query_engine.run()
