# Phantom Search Engine

Phantom Search Engine is a lightweight, distributed web search engine designed to provide fast and relevant search results.

## Features

- Distributed crawler system for efficient web crawling
- Multithreaded crawling for concurrent processing
- TF-IDF based indexing for faster search and retrieval
- Query engine for processing user queries and returning relevant results

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. Clone the repository:

```sh
git clone https://github.com/yourusername/phantom-search.git
cd phantom-search
```

2. Create a virtual environment and activate it:
```sh
python3 -m venv .env
source .env/bin/activate
```

3. Install the necessary dependencies:
```sh
pip install -r requirements.txt
```

## Building from Source

1. Run the build.sh script:

This script performs the following actions:
```sh
./build.sh
```
- Creates a virtual environment and activates it.
- Installs the necessary dependencies from the requirements.txt file.
- Runs the Phantom crawler with the specified parameters.
- Downloads the necessary NLTK packages: stopwords and punkt.
- Runs the Phantom indexing module.

2. Start the query engine locally in the terminal by running the search.sh file:
```sh
./search.sh
```

### Alternative Method

1. Run the `crawl.sh` file by updating necessary parameters
2. Run the `local_search.sh` to index the crawled sites and run the query engine on it

## Contributing
We welcome contributions! Please see our CONTRIBUTING.md for details on how to contribute to this project.

## License
This project is licensed under the terms of the Apache License. See the LICENSE file for details.
