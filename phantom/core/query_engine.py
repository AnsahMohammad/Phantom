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
            # content uses word2vec
            self.content_processor = Word2Vec_Processor()
            self.content_processor.load(filename)

        if self.IDF_TITLE:
            # title uses tfidf
            self.title_processor = TFIDF_Processor()
            title_name = "title_" + filename
            self.title_processor.load(title_name)

    def query(self, query, count=10):
        self.log(f"Query received : {query}", "Query_Engine")

        scores = defaultdict(float)

        if self.IDF_CONTENT:
            query_res = self.content_processor.query(query, count)
            for doc, score in query_res:
                scores[doc] += self.CONTENT_WEIGHT * score

        if self.IDF_TITLE:
            # title processed on tf-idf
            query_res = self.title_processor.query(query, count)
            for doc, score in query_res:
                scores[doc] += self.TITLE_WEIGHT * score
            
        ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        self.log(f"Ranked documents : {ranked_docs}", "Query_Engine")

        # Return the top n results
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


import json
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import numpy as np
from gensim.models import Word2Vec


class Processor:
    def __init__(self):
        self.logger = Logger(True, "Model_processor")
        self.log = self.logger.log

        self.log("Processor Ready", "Model_processor")

    def preprocess(self, data:str):
        processed_query = []
        try:
            words = data.split()
            for word in words:
                word = word.lower().translate(str.maketrans("", "", string.punctuation))
                processed_query.append(word)

        except Exception as e:
            self.logger.error(f"Error processing query: {e}", "QEngine-pre-process")
        
        return processed_query

    def load(self, filename):
        with open(filename + ".json", "r") as f:
            load_data = json.load(f)
            model = load_data["model"]
            data = load_data["data"]

        return model, data


    def query(self):
        self.log("Processing Data", "Model-preprocessor")


class TFIDF_Processor(Processor):
    def __init__(self):
        super().__init__()
        self.name = "tf_idf"

    def load(self, filename="indexed"):
        model, data = super().load(filename)
        if model != self.name:
            self.logger.error("Model mismatch", "tf_idf_processor")
            raise ValueError("Model mismatch")

        self.idf = data["idf"]
        self.tfidf = data["tfidf"]
        self.lookup = set(self.idf.keys())
        self.log("Data Loaded", "tf_idf_processor")

    def query(self, query, count = 10):
        super().query()
        query = self.preprocess(query)
        query = [term for term in query if term in self.lookup]
        query_freq = Counter(query)
        query_tfidf = {
            term: (query_freq[term] /  len(query)) * self.idf.get(term, 0.0)
            for term in query
        }
        self.log("Query processed", "tf-idf-processor-query")
        self.log(f"Title TF-idf of query : {query_tfidf}", "tf-idf-processor-query")

        scores = defaultdict(float)
        for doc, tfidf in self.tfidf.items():
            score = sum(tfidf[term] * query_tfidf.get(term, 0.0) for term in tfidf)
            scores[doc] = score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_n_scores = sorted_scores[:count]
        # tuple of [(doc, score),...]
        return top_n_scores


class Word2Vec_Processor(Processor):
    def __init__(self):
        super().__init__()
        self.name = "word2vec"

    def load(self, filename="indexed"):
        model, data = super().load(filename)
        if model != self.name:
            self.logger.error("Model mismatch", "word2vec_processor")
            raise ValueError("Model mismatch")

        self.model = Word2Vec.load(filename + ".model")
        self.lookup = set(self.model.wv.key_to_index)
        self.log("Word2Vec model loaded", "word2vec_processor-load")
        
        self.document_embedding = data["embeddings"]
        self.docs = data["docs"]
        self.log("Document embeddings loaded", "word2vec_processor-load")

    def query(self, query, count=10):
        super().query()
        query = self.preprocess(query)

        query_tokens = [word for word in query if word in self.lookup]
        if not query_tokens:
            print("None of the words in the query are in the model's vocabulary.")
            return None

        query_vector = np.mean([self.model.wv[token] for token in query_tokens if token in self.model.wv], axis=0)
        self.log("Query processed", "word2vec-processor-query")
        similarities = cosine_similarity([query_vector], self.document_embedding)
        top_n_indices = np.argsort(similarities[0])[-count:]
        top_n_similar_docs = [(self.docs[i], similarities[0][i]) for i in top_n_indices]
        top_n_similar_docs.sort(key=lambda x: x[1], reverse=True)
        # tuple of [(doc, score),...]
        return top_n_similar_docs

if __name__ == "__main__":
    query_engine = Phantom_Query("indexed", title_path="titles.json")
    query_engine.run()
