from .base import Model, Processor

from collections import Counter, defaultdict
import math
import json


class Tf_idf(Model):
    def __init__(self, filename="index", out="indexed", key="url", val="content"):
        super().__init__(filename, out, key, val)
        self.tf = {}
        self.idf = {}
        self.tfidf = {}

    def calculate_tf(self, data) -> dict:
        tf = {}
        self.log("Calculating TF", origin="calculate_tf")
        for doc, text in data.items():
            tf_text = Counter(text)
            for i in tf_text:
                tf_text[i] = tf_text[i] / float(len(text))
            tf[doc] = tf_text

        return tf

    def calculate_idf(self, tf: dict) -> dict:
        self.log("Calculating IDF", origin="calculate_idf")
        idf_text = Counter([word for doc in tf.values() for word in doc])
        for i in idf_text:
            idf_text[i] = math.log10(self.documents / float(idf_text[i]))
        idf = idf_text
        return idf

    def calculate_tfidf(self) -> dict:
        self.log("Calculating TF-IDF", origin="calculate_tfidf")
        self.tf = self.calculate_tf(self.data)
        self.idf = self.calculate_idf(self.tf)

        tfidf = {}
        for doc, tf_scores in self.tf.items():
            tfidf_scores = {}
            for term, tf_score in tf_scores.items():
                tfidf_scores[term] = tf_score * self.idf[term]
            tfidf[doc] = tfidf_scores

        self.tfidf = tfidf
        return tfidf

    def save(self):
        data = {"idf": self.idf, "tfidf": self.tfidf}
        with open(self.out_file + ".json", "w") as f:
            json.dump({"model": "tf_idf", "data": data}, f)
        self.log("Data Saved", origin="tfidf-save")


class TFIDF_Processor(Processor):
    def __init__(self):
        super().__init__()
        self.name = "tf_idf"

    def load(self, filename="indexed"):
        model, data = super().load(filename)
        if model != self.name:
            self.logger.error("Model mismatch", origin="tfidf-processor-loader")
            raise ValueError("Model mismatch")

        self.idf = data["idf"]
        self.tfidf = data["tfidf"]
        self.lookup = set(self.idf.keys())
        self.log("Data Loaded", origin="tfidf-processor-load")

    def query(self, query, count=10):
        super().query()
        query = self.preprocess(query)
        query = [term for term in query if term in self.lookup]
        query_freq = Counter(query)
        query_tfidf = {
            term: (query_freq[term] / len(query)) * self.idf.get(term, 0.0)
            for term in query
        }
        self.log("Query processed", origin="tfidf-processor-query")
        self.log(f"Title TF-idf of query : {query_tfidf}", origin="tfidf-processor-query")

        scores = defaultdict(float)
        for doc, tfidf in self.tfidf.items():
            score = sum(tfidf[term] * query_tfidf.get(term, 0.0) for term in tfidf)
            scores[doc] = score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_n_scores = sorted_scores[:count]
        # tuple of [(doc, score),...]
        return top_n_scores
