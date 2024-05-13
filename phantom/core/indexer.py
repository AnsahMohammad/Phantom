from collections import Counter
import math
import json
import string
from ..utils.logger import Logger
import os
from supabase import create_client, Client
from ..utils.storage import Database

# nltk.download('punkt')
# nltk.download('stopwords')


class PhantomIndexer:
    def __init__(
        self, filename="index", out="indexed") -> None:
        self.in_file = filename
        self.out_file = out

        self.showlogs = os.environ.get("SHOW_LOGS", "1") == "1"
        self.logger = Logger(self.showlogs, "Indexer")
        self.log = self.logger.log

        db = Database()
        if not db.state:
            self.log("Database not connected", "Phantom-Indexer")
            return

        self.log("indexer init", "Phantom-Indexer")

    def process(self, model="tf_idf", key="url", val="content"):

        self.log(
            f"Indexer called for in: {self.in_file}, out: {self.out_file}, key: {key}, val: {val} model: {model}",
        )

        if model == "tf_idf":
            self.model = tf_idf(self.in_file, self.out_file, key=key, val=val)

            tfidf = self.model.calculate_tfidf()
            idf = self.model.idf
        else:
            return
            self.model = word2vec(self.in_file, self.out_file)
            self.model.train_word2vec()

        return True

    def save(self):
        self.model.save()
        self.log("Data Saved", "Phantom-Indexer")

    def save_titles(self, filename="titles"):
        """store url:title mapping in local file"""
        self.log("Saving URL:Title mapping", "Phantom-Indexer")
        data = {url: title for url, title in self.model.raw_data.items()}
        with open(filename + ".json", "w") as f:
            json.dump(data, f)
        self.log(f"URL:Title mapping saved to {filename}.json", "Phantom-Indexer")


class Model:
    def __init__(self, filename="index", out="indexed", key="url", val="content"):
        self.in_file = filename
        self.out_file = out

        self.logger = Logger(True, "Model_processor")
        self.log = self.logger.log

        self.CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 500))

        database = Database()
        if not database.state:
            self.log("Database not connected", "Phantom-Indexer")
            return
        data = database.load(table=self.in_file, key=key, val=val)
        self.raw_data = data.copy()
        self.documents = len(data.keys())
        self.log("data fetched")
        self.data = self.preprocess(data)
        self.documents = len(self.data.keys())
        self.log("data pre-processed")

    def preprocess(self, data:dict) -> dict:
        self.log("Processing Data", "Model-preprocessor")
        count = 0
        processed_data = {}
        for doc, words in data.items():
            count += 1
            processed_words = []
            try:
                words = words.split()
                for word in words:
                    word = word.lower().translate(str.maketrans("", "", string.punctuation))
                    if len(word) < 30:
                        processed_words.append(word)
                if count % self.CHUNK_SIZE == 0:  # Log status
                    self.log(
                        f"Processed {round((count/self.documents)*100,2)}% documents",
                        "Phantom-Indexer",
                    )
                processed_data[doc] = processed_words
            except Exception as e:
                self.logger.error(
                    f"Error processing {doc}: {e}", "Phantom-Indexer-process"
                )
                continue

            del words

        self.log("Data Processed", "Phantom-Indexer")
        return processed_data

    def save(self, data):
        with open(self.out_file + ".json", "w") as f:
            json.dump(data, f)

class tf_idf(Model):
    def __init__(self, filename="index", out="indexed", key="url", val="content"):
        super().__init__(filename, out, key, val)
        self.tf = {}
        self.idf = {}
        self.tfidf = {}

    def calculate_tf(self, data) -> dict:
        tf = {}
        self.log("Calculating TF", "Phantom-Indexer")
        for doc, text in data.items():
            tf_text = Counter(text)
            for i in tf_text:
                tf_text[i] = tf_text[i] / float(len(text))
            tf[doc] = tf_text
        
        return tf

    def calculate_idf(self, tf: dict) -> dict:
        self.log("Calculating IDF", "Phantom-Indexer")
        idf_text = Counter([word for doc in tf.values() for word in doc])
        for i in idf_text:
            idf_text[i] = math.log10(self.documents / float(idf_text[i]))
        idf = idf_text
        return idf

    def calculate_tfidf(self) -> dict:
        self.log("Calculating TF-IDF", "Phantom-Indexer")
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
            json.dump({'model': 'tf_idf', 'data': data}, f)
        self.log("Data Saved", "Phantom-Indexer-tf_idf")

class word2vec(Model):
    def __init__(self, filename="index", out="indexed"):
        super().__init__(filename, out)

    def train_word2vec(self):
        pass

    def save(self, data):
        with open(self.out_file + ".json", "w") as f:
            json.dump({'model': 'word2vec', 'data': data}, f)

IDF_CONTENT = os.environ.get("IDF_CONTENT", "1") == "1"
IDF_TITLE = os.environ.get("IDF_TITLE", "1") == "1"

if IDF_CONTENT:
    processor = PhantomIndexer("index", out="indexed")
    processor.process()
    processor.save()
    print("Indexing content completed!")

if IDF_TITLE:
    processor = PhantomIndexer("index", out="title_indexed")
    processor.process(model="tf_idf", key="url", val="title")
    processor.save()
    processor.save_titles("titles")
    print("Indexing titles completed!")
