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
