from collections import Counter
import math
import json
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import string
from .logger import Logger


# nltk.download('punkt')
# nltk.download('stopwords')


class PhantomIndexer:
    def __init__(self, filename="index.json", out="indexed.json") -> None:
        self.out_file = out
        self.in_file = filename

        self.data = {}
        with open(self.in_file, "r") as f:
            self.data = json.load(f)

        self.documents = len(self.data.keys())
        self.tf = {}
        self.idf = {}
        self.tfidf = {}
        self.showlogs = True

        self.logger = Logger(self.showlogs)
        self.log = self.logger.log

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

        for doc, words in self.data.items():
            processed_words = []
            for word in words:
                word = word.lower().translate(str.maketrans("", "", string.punctuation))
                if word not in stop_words and len(word) < 30:
                    stemmed_word = stemmer.stem(word)
                    processed_words.append(stemmed_word)
            self.data[doc] = processed_words

        self.log("Data Processed", "Phantom-Indexer")

        self.calculate_tfidf()

        for doc in self.tfidf:
            self.tfidf[doc] = dict(
                sorted(self.tfidf[doc].items(), key=lambda x: x[1], reverse=True)
            )

        return self.tfidf

    def save(self):
        # data = {"tfidf": self.tfidf, "idf": self.idf, "tf": self.tf}
        data = {"tfidf": self.tfidf, "idf": self.idf}
        with open(self.out_file, "w") as f:
            json.dump(data, f)

        self.log("Data Saved", "Phantom-Indexer")


processor = PhantomIndexer("index.json")
processor.process()
processor.save()
print("Indexing completed!")
