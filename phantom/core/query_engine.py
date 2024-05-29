import json
from collections import defaultdict
from ..utils.logger import Logger
from ..utils.storage import Database

from .models.tf_idf import TFIDF_Processor
from .models.word2vec import Word2Vec_Processor

import os

import string


class Phantom_Query:
    def __init__(self, filename="indexed", title_path=None):

        self.showlogs = True
        self.title_table = False
        self.logger = Logger(self.showlogs, author="query_engine-Phantom_Query")
        self.log = self.logger.log

        db = Database()
        self.remote_db = db.state

        self.IDF_CONTENT = os.environ.get("IDF_CONTENT", "1") == "1"
        self.IDF_TITLE = os.environ.get("IDF_TITLE", "1") == "1"
        self.CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 500))
        self.CHUNK_LIMIT = int(os.environ.get("CHUNK_LIMIT", 10000))

        self.log(
            f"Query Engine called for in: {filename}\n IDF_CONTENT: {self.IDF_CONTENT}\n IDF_TITLE: {self.IDF_TITLE}",
            origin="init",
        )

        self.CONTENT_WEIGHT = int(os.environ.get("CONTENT_WEIGHT", 1))
        self.TITLE_WEIGHT = int(os.environ.get("TITLE_WEIGHT", 2))
        self.TIME_WEIGHT = int(os.environ.get("TIME_WEIGHT", 5))

        self.data = {}
        self.load(filename)

        if title_path or self.remote_db:
            self.title_path = title_path
            self.title_table = True
            self.titles = {}
            if not self.load_titles():
                self.log("Failed to load titles", origin="init")
                self.title_table = False
            else:
                self.log("Titles loaded", origin="init")

        self.log("Query Engine Ready", origin="init")

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
        self.log(f"Query received : {query}", origin="query")

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
        self.log(f"Ranked documents : {ranked_docs}", origin="query")

        # Return the top n results
        final_results = []
        for doc, score in ranked_docs[:count]:
            
            # send only if score > 0
                # Hence may get results < count
            if score == 0:
                continue

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
            self.log("Loading data from local file", origin="load_titles")
            with open(self.title_path, "r") as f:
                self.titles = json.load(f)
            self.log(f"Data loaded from local file: {len(self.titles)}", origin="load_titles")
            return True

        elif self.remote_db:
            """TODO: Fetch data from remote DB using Database and not explicitly"""
            try:
                self.log("Fetching data from remote DB", origin="load_titles")
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
                        origin="load_titles",
                    )

                    if len(self.titles) > self.CHUNK_LIMIT:
                        self.log("CHUNK limit reached", origin="load_titles")
                        break

                self.log(
                    f"Data fetched from remote DB: {len(self.titles)}",
                    origin="load_titles",
                )
            except Exception as e:
                self.logger.error(
                    f"Error fetching data from index table: {e}",
                    origin="load_titles",
                )
                return False
            return True

        else:
            if not self.title_path:
                return False


if __name__ == "__main__":
    query_engine = Phantom_Query("indexed", title_path="titles.json")
    query_engine.run()
