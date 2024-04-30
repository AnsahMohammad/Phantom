import json
from collections import Counter
from logger import Logger

class Phantom_Query:
    def __init__(self, filename=None):

        self.showlogs = True

        self.data = {}
        with open(filename, "r") as f:
            self.data = json.load(f)
        
        self.tf = self.data["tf"]
        self.idf = self.data["idf"]
        self.tfidf = self.data["tfidf"]
        
        self.logger = Logger(self.showlogs)
        self.log = self.logger.log

        self.lookup = set(self.idf.keys())

    def query(self, query):
        self.log(f"Query recieved : {query}", "Query_Engine")
        query = query.split()
        query_len = len(query)
        query = [term for term in query if term in self.lookup]
        query_freq = Counter(query)
        query_tfidf = {term: (query_freq[term]/query_len) * self.idf[term] for term in query}

        self.log(f"TF-idf of query : {query_tfidf}", "Query_Engine")

        scores = {}
        for doc, tfidf in self.tfidf.items():
            score = sum(tfidf[term] * query_tfidf.get(term, 0.0) for term in tfidf)
            scores[doc] = score

        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        self.log(f"Ranked documents : {ranked_docs}", "Query_Engine")

        return ranked_docs


phant = Phantom_Query("indexed.json")

while True:
    query = input("Enter the query : ")
    print(phant.query(query))

