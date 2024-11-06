# OC-P2

This program is used to extract data from books on the site http://books.toscrape.com/index.html

## Requirements

- Python 3.x
- pip

## Setup

### 1. Clone the repository

Open your terminal and clone the project repository using the following command:

    git clone https://github.com/QuentinSab/OC-P2.git

Change into the project directory:

    cd OC-P2

### 2. Create a virtual environment

To create a virtual environment with venv:

    python -m venv env

### 3. Activate the virtual environment

To activate the virtual environment, use:

On Windows:

    env\Scripts\activate

On macOS/Linux:

    source env/bin/activate

### 4. Install dependencies

With the virtual environment activated, install the required packages listed in requirements.txt using the following command:

    pip install -r requirements.txt

## Usage

### 1. Running the program for all books

Run main.py without any arguments to extract data for all books on the site:

    python main.py

### 2. Running the program for a single category

To extract data from a specific category only, run main.py with the category URL as an argument:

    python main.py http://books.toscrape.com/catalogue/category/books/example-category/index.html