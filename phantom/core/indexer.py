import json
from ..utils.logger import Logger
import os
from ..utils.storage import Database

from .models.tf_idf import Tf_idf
from .models.word2vec import Word2vec


class PhantomIndexer:
    def __init__(self, filename="index", out="indexed") -> None:
        self.in_file = filename
        self.out_file = out

        self.showlogs = os.environ.get("SHOW_LOGS", "1") == "1"
        self.logger = Logger(self.showlogs, "Indexer")
        self.log = self.logger.log

        db = Database()
        if not db.state:
            self.log("Database not connected", author="indexer-PhantomIndexer")
            return

        self.log("indexer init", origin="init")

    def process(self, model="tf_idf", key="url", val="content"):

        self.log(
            f"Indexer called for in: {self.in_file}, out: {self.out_file}, key: {key}, val: {val} model: {model}",
            origin="process",
        )

        if model == "tf_idf":
            self.model = Tf_idf(self.in_file, self.out_file, key=key, val=val)

            tfidf = self.model.calculate_tfidf()
            idf = self.model.idf
        elif model == "word2vec":
            self.model = Word2vec(self.in_file, self.out_file)
            self.model.train_word2vec()
        else:
            self.log("Invalid model", origin="process")
            return False

        return True

    def save(self):
        self.model.save()

        # self.model.test("water is very important")
        self.log("Data Saved", origin="save")

    def save_titles(self, filename="titles"):
        """store url:title mapping in local file"""
        self.log("Saving URL:Title mapping", origin="save_titles")
        data = {url: title for url, title in self.model.raw_data.items()}
        with open(filename + ".json", "w") as f:
            json.dump(data, f)
        self.log(f"URL:Title mapping saved to {filename}.json", origin="save_titles")


IDF_CONTENT = os.environ.get("IDF_CONTENT", "1") == "1"
IDF_TITLE = os.environ.get("IDF_TITLE", "1") == "1"

if IDF_CONTENT:
    processor = PhantomIndexer("index", out="indexed")
    processor.process(model="word2vec", key="url", val="content")
    processor.save()
    print("Indexing content completed!")

if IDF_TITLE:
    processor = PhantomIndexer("index", out="title_indexed")
    processor.process(model="tf_idf", key="url", val="title")
    processor.save()
    processor.save_titles("titles")
    print("Indexing titles completed!")
