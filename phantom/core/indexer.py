from collections import Counter
import math
import json
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import string
from ..utils.logger import Logger
import os
from supabase import create_client, Client

# nltk.download('punkt')
# nltk.download('stopwords')


class PhantomIndexer:
    def __init__(
        self, filename="index", out="indexed", key="url", val="content"
    ) -> None:
        self.in_file = filename
        self.out_file = out

        self.showlogs = True
        self.logger = Logger(self.showlogs, "Indexer")
        self.log = self.logger.log
        self.remote_db = self.check_remote()
        self.CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 500))
        self.CHUNK_LIMIT = int(os.environ.get("CHUNK_LIMIT", 10000))

        self.log(
            f"Indexer called for in: {self.in_file} out: {self.out_file}, key: {key}, val: {val}"
        )
        self.data = self.load(key=key, val=val)
        self.remote_data = self.data.copy()
        if not self.data:
            # if remote cause error, load from local
            self.remote_db = False
            self.data = self.load()

        self.documents = len(self.data.keys())
        self.tf = {}
        self.idf = {}
        self.tfidf = {}

    def calculate_tf(self):
        self.log("Calculating TF", "Phantom-Indexer")
        for doc, text in self.data.items():
            tf_text = Counter(text)
            for i in tf_text:
                tf_text[i] = tf_text[i] / float(len(text))
            self.tf[doc] = tf_text

    def calculate_idf(self):
        self.log("Calculating IDF", "Phantom-Indexer")
        idf_text = Counter([word for doc in self.tf.values() for word in doc])
        for i in idf_text:
            idf_text[i] = math.log10(self.documents / float(idf_text[i]))
        self.idf = idf_text

    def calculate_tfidf(self):
        self.log("Calculating TF-IDF", "Phantom-Indexer")
        self.calculate_tf()
        self.calculate_idf()
        for doc, tf_scores in self.tf.items():
            tfidf_scores = {}
            for term, tf_score in tf_scores.items():
                tfidf_scores[term] = tf_score * self.idf[term]
            self.tfidf[doc] = tfidf_scores

    def process(self):
        self.log("Processing Data", "Phantom-Indexer")
        stemmer = PorterStemmer()
        stop_words = set(stopwords.words("english"))
        count = 0
        for doc, words in self.data.items():
            count += 1
            processed_words = []
            try:
                words = word_tokenize(words)
                for word in words:
                    word = word.lower().translate(
                        str.maketrans("", "", string.punctuation)
                    )
                    if word not in stop_words and len(word) < 30:
                        stemmed_word = stemmer.stem(word)
                        processed_words.append(stemmed_word)
                if count % self.CHUNK_SIZE == 0:  # Log status
                    self.log(
                        f"Processed {round((count/self.documents)*100,2)}% documents",
                        "Phantom-Indexer",
                    )
                self.data[doc] = processed_words
            except Exception as e:
                self.logger.error(
                    f"Error processing {doc}: {e}", "Phantom-Indexer-process"
                )

            del words

        self.log("Data Processed", "Phantom-Indexer")

        self.calculate_tfidf()

        for doc in self.tfidf:
            self.tfidf[doc] = dict(
                sorted(self.tfidf[doc].items(), key=lambda x: x[1], reverse=True)
            )

        return self.tfidf

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
            self.logger.error(
                f"Error while creating Supabase client: {e}",
                "Phantom-Indexer-check_remote",
            )
            remote_db = False

        print("Remote database : ", remote_db)
        print("DB Ready")
        return remote_db

    def load(self, key="url", val="content"):
        # load the index.json
        data = {}
        if self.remote_db:
            try:
                self.log("Fetching data from remote DB")
                start = 0
                end = self.CHUNK_SIZE - 1
                while True:
                    response = (
                        self.supabase.table(self.in_file)
                        .select(key, val)
                        .range(start, end)
                        .execute()
                    )
                    if not response.data:
                        break
                    for record in response.data:
                        data[record[key]] = record[val]
                    start += self.CHUNK_SIZE
                    end += self.CHUNK_SIZE
                    self.log(
                        f"Data fetched from remote DB: {len(data)}",
                        "Phantom-Indexer-Loader",
                    )

                    if len(data) > self.CHUNK_LIMIT:
                        self.log("CHUNK limit reached", "Phantom-Indexer-Loader")
                        break

                self.log(
                    f"Data fetched from remote DB: {len(data)}",
                    "Phantom-Indexer-Loader",
                )
            except Exception as e:
                self.logger.error(
                    f"Error fetching data from index table: {e}",
                    "Phantom-Indexer-Loader",
                )
                if len(data) > 500:
                    return data
                return None

        else:
            self.log("Loading data from local file")
            with open(self.in_file + ".json", "r") as f:
                data = json.load(f)

        return data

    def save(self):
        # data = {"tfidf": self.tfidf, "idf": self.idf, "tf": self.tf}
        data = {"tfidf": self.tfidf, "idf": self.idf}
        with open(self.out_file + ".json", "w") as f:
            json.dump(data, f)

        self.log("Data Saved", "Phantom-Indexer")

    def save_titles(self, filename="titles"):
        """store url:title mapping in local file"""
        if not self.remote_db:
            self.log("Remote DB not connected, cannot save titles", "Phantom-Indexer")
            return

        data = {url: title for url, title in self.remote_data.items()}
        with open(filename + ".json", "w") as f:
            json.dump(data, f)
        self.log(f"URL:Title mapping saved to {filename}.json", "Phantom-Indexer")


IDF_CONTENT = os.environ.get("IDF_CONTENT", "1") == "1"
IDF_TITLE = os.environ.get("IDF_TITLE", "1") == "1"

if IDF_CONTENT:
    processor = PhantomIndexer("index", out="indexed")
    processor.process()
    processor.save()
    print("Indexing content completed!")

if IDF_TITLE:
    processor = PhantomIndexer("index", out="title_indexed", key="url", val="title")
    processor.process()
    processor.save()
    processor.save_titles("titles")
    print("Indexing titles completed!")
