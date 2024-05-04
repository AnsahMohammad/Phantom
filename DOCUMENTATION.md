# The Documentation

# Phantom Search Engine

Phantom Search Engine is a robust, scalable, and efficient web search engine designed to provide fast and relevant search results. It is built with a focus on performance, scalability, and accuracy. The engine is designed to handle a large amount of data and provide quick responses to user queries.

The Phantom Search Engine consists of several main components:

1. **Crawler System**: The Crawler System is responsible for crawling the web and fetching the content of web pages. It includes a multithreaded crawler for concurrent crawling and a distributed crawler system for large-scale crawling.

2. **Phantom Indexer**: The Phantom Indexer processes the fetched data to create an index for faster search and retrieval. It uses the TF-IDF (Term Frequency-Inverse Document Frequency) algorithm to measure the importance of a term in a document in a corpus.

3. **Phantom Query Engine**: The Phantom Query Engine is a crucial component that takes a user's search query and returns the most relevant documents from the database. It uses the TF-IDF algorithm to rank the documents based on their relevance to the query.

Each of these components is designed to work together seamlessly to provide a comprehensive search engine solution. The following sections provide a detailed overview of each component and how they interact with each other.

This documentation is intended to provide a comprehensive understanding of the Phantom Search Engine's architecture, functionality, and usage. It is designed to be a valuable resource for developers, users, and anyone interested in understanding the inner workings of a web search engine.

# Crawler system

There are two ways you can crawl the websites to save the indexes
1) Multithreaded approach
2) Distributed Crawler system

## 1) Multithreaded Crawlers

The multithreaded crawler is implemented in the `Phantom` class in the `src/phantom.py` file. It uses multiple threads to crawl websites concurrently, which significantly speeds up the crawling process.

Here's a brief overview of how it works:

- The `Phantom` class is initialized with a list of URLs to crawl, the number of threads to use, and other optional parameters like whether to show logs, print logs, and a burnout time after which the crawler stops.

- The `run` method starts the crawling process. It generates the specified number of threads and starts them. Each thread runs the `crawler` method with a unique ID and a randomly chosen URL from the provided list.

- The `crawler` method is the heart of the crawler. It starts with a queue containing the initial URL and continuously pops URLs from the queue, fetches their content, and adds their neighbors (links on the page) to the queue. It also keeps track of visited URLs to avoid revisiting them. The content of each visited URL is stored in a `Storage` object.

- The `Parser` class is used to fetch and parse the content of a URL. It uses the BeautifulSoup library to parse the HTML content, extract the text and the links, and clean the URLs.

- The `Storage` class is used to store the crawled data. It stores the data in a dictionary and can save it to a JSON file.

- The `stop` method can be used to stop the crawling process. It sets a `kill` flag that causes the `crawler` methods to stop, waits for all threads to finish, and then saves the crawled data and prints some statistics.

You can start the program by running the script on `src/phantom.py`. It uses `phantom_engine.py` to crawl the sites using multiple threads.


## 2) Distributed Crawler system

The distributed crawler system uses a master-slave architecture to coordinate multiple crawlers. The master node is implemented in the `phantom_master.py` file, and the slave nodes are implemented in the `phantom_child.py` file. They communicate using sockets.

### Phantom Master

The `phantom_master.py` file contains the `Server` class, which is the master node in the distributed crawler system. It manages the slave nodes (crawlers) and assigns them websites to crawl.

Here's a brief overview:

- The `Server` class is initialized with the host and port to listen on, the number of clients (crawlers) to accept, and a burnout time after which the crawlers stop.

- The `run` method starts the server. It creates a socket, binds it to the specified host and port, and starts listening for connections. It accepts connections from the crawlers, starts a new thread to handle each crawler, and adds the crawler to its list of clients.

- The `handle_client` method is used to handle a crawler. It continuously receives requests from the crawler and processes them. If a crawler sends a "close" request, it removes the crawler from its list of clients. If a crawler sends a "status" request, it updates its status.

- The `status` method is used to print the status of the server and the crawlers. It prints the list of crawlers and their statuses.

- The `send_message` method is used to send a message to a specific crawler. If an error occurs while sending the message, it removes the crawler from its list of clients.

- The `assign_sites` method is used to assign websites to the crawlers. It either assigns each website to a different crawler or assigns all websites to all crawlers, depending on the `remove_exist` parameter.

- The `generate` method is used to generate the websites to crawl. It asks the user to enter the websites, assigns them to the crawlers, and starts the crawlers.

- The `start` method is used to start the server. It starts the server in a new thread and then enters a command loop where it waits for user commands. The user can enter commands to get the status of the server, broadcast a message to all crawlers, send a message to a specific crawler, stop the server, generate websites, assign websites to crawlers, and merge the crawled data.

- The `merge` method is used to merge the data crawled by the crawlers. It merges the index and title data from all crawlers into a single index and title file and deletes the old files.

- The `stop` method is used to stop the server. It sends a "stop" message to all crawlers, stops the server thread, and closes the server socket.

You can start the server by running the `phantom_master.py` script. It will start listening for connections from crawlers and you can then enter commands to control the crawlers.

### Phantom Child

The `phantom_child.py` file contains the `Crawler` and `Storage` classes, which implement the slave nodes in the distributed crawler system. 

Here's a brief overview:

- The `Crawler` class is initialized with the host and port of the server. It creates a socket and connects to the server. It also initializes several other attributes, such as its ID, a list of threads, and several flags.

- The `connect` method is used to connect the crawler to the server. It starts a new thread to listen to the server and enters a command loop where it waits for user commands. The user can enter commands to stop the crawler, send a message to the server, get the status of the crawler, toggle the running state of the crawler, and store the crawled data.

- The `listen_to_server` method is used to listen to the server. It continuously receives messages from the server and processes them. If the server sends a "stop" message, it stops the crawler. If the server sends a "setup" message, it sets up the crawler. If the server sends a "status" message, it prints the status of the crawler. If the server sends an "append" message, it adds URLs to the queue. If the server sends a "restart" message, it reinitializes the crawler. If the server sends a "crawl" message, it starts crawling.

- The `setup` method is used to set up the crawler. It sets the URL to crawl and the burnout time.

- The `add_queue` method is used to add URLs to the queue.

- The `initialize` method is used to initialize the crawler. It initializes several attributes, such as the list of local URLs, the queue, the start time, and the parser.

- The `crawl` method is used to start crawling. It continuously pops URLs from the queue, parses them, and adds the parsed data to the storage. It also adds the neighbors of the current URL to the queue. If the burnout time is reached, it stops crawling.

- The `store` method is used to store the crawled data. It saves the index and title data to the storage.

- The `stop` method is used to stop the crawler. It sets the kill flag, clears the traversed URLs, joins all threads, sends a "close" message to the server, and closes the client socket.

- The `send` method is used to send a message to the server.

- The `status` method is used to print the status of the crawler.

- The `Storage` class is used to store the crawled data. It is initialized with a filename and a dictionary to store the data. The `add` method is used to add data to the storage. The `save` method is used to save the data to a file.

You can start a crawler by creating an instance of the `Crawler` class and calling the `connect` method. The crawler will connect to the server and start listening for commands.


# Phantom Indexer

The `PhantomIndexer` class in the provided code is an implementation of an indexer. An indexer is a program that processes data (in this case, text documents) to create an index for faster search and retrieval. The index created by the `PhantomIndexer` is based on the TF-IDF (Term Frequency-Inverse Document Frequency) algorithm, a common algorithm used in information retrieval.

Here's a brief overview of the `PhantomIndexer` class:

- The `__init__` method initializes the indexer. It takes as input the name of the input file (`filename`) and the name of the output file (`out`). It also initializes several other attributes, such as the total number of documents (`documents`), the term frequency (`tf`), the inverse document frequency (`idf`), and the TF-IDF (`tfidf`).

- The `calculate_tf` method calculates the term frequency for each term in each document. The term frequency is the number of times a term appears in a document.

- The `calculate_idf` method calculates the inverse document frequency for each term. The inverse document frequency is a measure of how much information the term provides, i.e., if it's common or rare across all documents.

- The `calculate_tfidf` method calculates the TF-IDF for each term in each document. The TF-IDF is the product of the term frequency and the inverse document frequency. It is a measure of the importance of a term in a document in a corpus.

- The `process` method processes the data. It tokenizes the text, removes stop words, stems the words, and calculates the TF-IDF.

- The `save` method saves the TF-IDF and IDF to a file.

- The `log` method is used to log messages.

The `PhantomIndexer` class is used as follows:

1. An instance of the `PhantomIndexer` class is created with the input file name and the output file name.

2. The `process` method is called to process the data and calculate the TF-IDF.

3. The `save` method is called to save the TF-IDF and IDF to a file.

The output of the `PhantomIndexer` is a JSON file that contains the TF-IDF and IDF for each term in each document. This file can be used for fast search and retrieval of documents.

# Phantom Query Engine

The `Phantom_Query` class in the provided code is an implementation of a query engine. A query engine is a crucial component of a search engine that takes a user's search query and returns the most relevant documents from the database. The `Phantom_Query` class uses the TF-IDF (Term Frequency-Inverse Document Frequency) algorithm to rank the documents based on their relevance to the query.

Here's a brief overview of the `Phantom_Query` class:

- The `__init__` method initializes the query engine. It takes as input the name of the input file (`filename`) and the name of the titles file (`titles`). It also initializes several other attributes, such as the inverse document frequency (`idf`), the TF-IDF (`tfidf`), and a lookup set of all terms in the corpus.

- The `query` method takes a user's search query and returns the most relevant documents. It first splits the query into terms and filters out the terms that are not in the lookup set. It then calculates the TF-IDF for each term in the query. Next, it calculates the score for each document by summing the product of the TF-IDF of each term in the document and the TF-IDF of the same term in the query. Finally, it ranks the documents based on their scores and returns the top `count` documents.

- The `run` method starts the query engine. It continuously prompts the user to enter a query and prints the results of the query.

- The `log` method is used to log messages.

The `Phantom_Query` class is used as follows:

1. An instance of the `Phantom_Query` class is created with the input file name and the titles file name.

2. The `run` method is called to start the query engine.

The output of the `Phantom_Query` class is a list of tuples, where each tuple contains the document ID, the score, and the title of a document. The list is sorted in descending order of the scores, so the first tuple corresponds to the most relevant document.


### Use of remote database
In this application, `supabase` has been used, inorder to leverage the supabase, user will have to create an account, and create two tables

1. Table **index** with the following fields:
- url (text)
- content (json)
- title (text)

2. Table **query** with the fields
- query(text)

The query table is used to store the queries to take analyse the queries made