# Phantom Search Engine

[![Python](https://img.shields.io/badge/Python-3.8%20%7C%203.9%20%7C%203.10-informational)](https://www.python.org/)
[![License](https://img.shields.io/github/license/qiskit-community/quantum-prototype-template?label=License)](https://github.com/IceKhan13/purplecaffeine/blob/main/LICENSE)
[![Code style: Black](https://img.shields.io/badge/Code%20style-Black-000.svg)](https://github.com/psf/black)
[![Crawler Test](https://github.com/AnsahMohammad/Phantom/actions/workflows/crawl.yaml/badge.svg)](https://github.com/AnsahMohammad/Phantom/actions/workflows/crawl.yaml)
![Deploy Status](https://img.shields.io/website?down_color=red&down_message=offline&up_color=green&up_message=online&url=https%3A%2F%2Fphantom-f6le.onrender.com)

Phantom Search Engine is a lightweight, distributed web search engine designed to provide fast and relevant search results.

![Phantom Demo](static/phantom_demo.gif)

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
git clone https://github.com/AnsahMohammad/Phantom.git
cd Phantom
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

4. Build the files:
```sh
./build.sh
```

5. Open the Search Engine GUI
```python
python phantom.py
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

> **Note:** Read the [documentation here](./DOCUMENTATION.md)

## Contributing
We welcome contributions! Please see our CONTRIBUTING.md for details on how to contribute to this project.

## License
This project is licensed under the terms of the Apache License. See the LICENSE file for details.


## Development and Maintanence

### Bump 0.9.1

- [ ] Error handling
- [ ] Consistency in logs
- [ ] Local db enable

### Bump 0.10+

- [ ] Distributed query processing
- [ ] Caching locally
- [ ] Two layer crawling
- [ ] Optimize the scheduler by storing visited nodes
- [ ] Use unified crawler system in master-slave arch
- [ ] Create Storage abstraction classes for local and remote client

### Bump 9

- [X] TF-idf only on title
- [X] Better similarity measure on content
- [X] Generalize Storage Class

### Bump 8

- [X] Optimize the deployment
- [X] Remove the nltk processing
- [X] Refactor the codebase
- [X] Migrate from local_db to cloud Phase-1
- [X] Optimize the user interface

### Bump 7

- [X] Replace content with meta data (perhaps?)
- [X] Extract background worker sites from env
- [X] AI support Beta
- [X] Template optimizations

### Bump 6

- [ ] Extract timestamp and sort accordingly
- [X] Remote crawler service (use background workers)
- [X] Analyze the extractable metadata
- [X] Error Logger to supabase for analytics

### Bump 5-

- [X] Don't download everytime query engine is started
- [ ] Crawler doesn't follow the schema of remote_db
- [X] Tracking variables on the server
- [X] UI Re-org
- [X] Title TF_IDF
- [X] Join contents with .join(" ")
- [X] Optimize parser to extract data effectively
- [X] Add tests

