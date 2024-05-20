from .base import Model, Processor
import json

from gensim.models import Word2Vec
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class Word2vec(Model):
    def __init__(self, filename="index", out="indexed", key="url", val="content"):
        super().__init__(filename, out, key, val)
        self.model = None

    def train_word2vec(self):
        self.log("Training Word2Vec", origin="train_word2vec")
        sentences = list(self.data.values())
        self.model = Word2Vec(sentences, min_count=1, window=5)
        self.log("Word2Vec trained", origin="train_word2vec")

    def test(self, query):
        self.log(f"Testing Word2Vec with query: {query}", origin="test")
        self.load_model()
        result = self.run_query(query)
        self.log(f"Result: {result}", origin="test")

    def save(self):
        if self.model:
            self.model.save(self.out_file + ".model")
            self.log("Word2Vec model saved", origin="save")

            self.log("saving document embeddings", origin="save")
            sentences = self.data.values()
            docs = self.data.keys()
            document_embeddings = []
            for doc_tokens in sentences:
                vectors = [
                    self.model.wv[token]
                    for token in doc_tokens
                    if token in self.model.wv
                ]
                if vectors:
                    doc_vector = np.mean(vectors, axis=0)
                else:
                    doc_vector = np.zeros(self.model.vector_size)
                document_embeddings.append(doc_vector.tolist())

            save_data = {"embeddings": document_embeddings, "docs": list(docs)}

            with open(self.out_file + ".json", "w") as f:
                json.dump({"model": "word2vec", "data": save_data}, f)

        else:
            self.log("No model to save", origin="save")


class Word2Vec_Processor(Processor):
    def __init__(self):
        super().__init__()
        self.name = "word2vec"

    def load(self, filename="indexed"):
        model, data = super().load(filename)
        if model != self.name:
            self.logger.error("Model mismatch", origin="word2vec_processor-loader")
            raise ValueError("Model mismatch")

        self.model = Word2Vec.load(filename + ".model")
        self.lookup = set(self.model.wv.key_to_index)
        self.log("Word2Vec model loaded", origin="word2vec_processor-load")

        self.document_embedding = data["embeddings"]
        self.docs = data["docs"]
        self.log("Document embeddings loaded", origin="word2vec_processor-load")

    def query(self, query, count=10):
        super().query()
        query = self.preprocess(query)

        query_tokens = [word for word in query if word in self.lookup]
        if not query_tokens:
            print("None of the words in the query are in the model's vocabulary.")
            return [(doc, -1) for doc in self.docs[:count]]

        query_vector = np.mean(
            [self.model.wv[token] for token in query_tokens if token in self.model.wv],
            axis=0,
        )
        self.log("Query processed", origin="word2vec-processor-query")
        similarities = cosine_similarity([query_vector], self.document_embedding)
        top_n_indices = np.argsort(similarities[0])[-count:]
        top_n_similar_docs = [(self.docs[i], similarities[0][i]) for i in top_n_indices]
        top_n_similar_docs.sort(key=lambda x: x[1], reverse=True)
        # tuple of [(doc, score),...]
        return top_n_similar_docs
