"""
Base class used by the models
"""

import os
import string
import json

from ...utils.logger import Logger
from ...utils.storage import Database


class Model:
    def __init__(self, filename="index", out="indexed", key="url", val="content"):
        self.in_file = filename
        self.out_file = out

        self.logger = Logger(True, "Model_processor")
        self.log = self.logger.log

        self.CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 500))

        database = Database()
        if not database.state:
            self.log("Database not connected", "Model")
            return
        data = database.load(table=self.in_file, key=key, val=val)
        self.raw_data = data.copy()
        self.documents = len(data.keys())
        self.log("data fetched")
        self.data = self.preprocess(data)
        self.documents = len(self.data.keys())
        self.log("data pre-processed")

    def preprocess(self, data: dict) -> dict:
        self.log("Processing Data", "Model-preprocessor")
        count = 0
        processed_data = {}
        for doc, words in data.items():
            count += 1
            processed_words = []
            try:
                words = words.split()
                for word in words:
                    word = word.lower().translate(
                        str.maketrans("", "", string.punctuation)
                    )
                    if len(word) < 30:
                        processed_words.append(word)
                if count % self.CHUNK_SIZE == 0:  # Log status
                    self.log(
                        f"Processed {round((count/self.documents)*100,2)}% documents",
                        "model-preprocess",
                    )
                processed_data[doc] = processed_words
            except Exception as e:
                self.logger.error(f"Error processing {doc}: {e}", "model-preprocess")
                continue

            del words

        self.log("Data Processed", "model-preprocess")
        return processed_data

    def test(self, a="0"):
        pass

    def save(self, data):
        try:
            with open(self.out_file + ".json", "w") as f:
                json.dump(data, f)
        except:
            self.logger.error(
                "Error while saving",
            )


class Processor:
    def __init__(self):
        self.logger = Logger(True, "Model_processor")
        self.log = self.logger.log

        self.log("Processor Ready", "Model_processor")

    def preprocess(self, data: str):
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
