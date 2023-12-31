# WIP: Annabel_trading
A WIP trading robot for automating investment process.
It's initially a command line tool that interacts with DEGIRO platform using DEGIRO connector.
Livermore pyramiding is, and will be the the main trading strategy behind this project.

# TODO:
Design document
- C4

Functional:
- code & implement Jesse Lauriston Livermore rules of trading, unit testing to gurantee the logics 
- read https://www.investopedia.com/articles/trading/09/legendary-trader-jesse-livermore.asp
- read RSI (relative strength index) divergence: https://www.investopedia.com/ask/answers/012915/what-are-best-technical-indicators-complement-relative-strength-index-rsi.asp
- combine livermore and RSI divergence

Technical:
- data streaming, long running? https://softlandia.fi/en/blog/real-time-data-processing-with-python-technology-evaluation
- async & multiprocessing (multiple stocks in the same time)
- separate quotecast api from trading operator

- encrypted password
- docstrings
- a good README
- mocked technical testing
- abstract get_orders_history & get_transactions_history

# Test:
- poetry run pytest --cov-report html:cov_html --cov=. tests/
- python -m http.server
- check report in browser: http://localhost:8000/cov_html/


# Virtualize:
- docker build -t annabel_trading --rm .
- docker run -it --rm annabel_trading
- push to goolge cloud:
    docker build -t eu.gcr.io/avian-volt-391821/annabel_trading:v1 --rm .
    docker push eu.gcr.io/avian-volt-391821/annabel_trading:v1
    gcrane cp -r eu.gcr.io/avian-volt-391821 europe-docker.pkg.dev/avian-volt-391821/eu.gcr.io


# Acknowledgement
I would like to pay tribute to Mr. Livermore from this childish app with respect. Meanwhile big thanks to Chavithra's great work: https://github.com/Chavithra/degiro-connector. Last but not least, thanks to my beloved daughters: Annie & Bella
