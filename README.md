# TravelSearch

Information Retreival Project on Search Engine

### Installing Dependencies
```
$ pip3 install -r requirements.txt
```

## Crawling Data

Maintainer: [@prajjwal1](https://github.com/prajjwal1)
```
$ cd crawl
$ scrapy crawl travel -O travel.json
```
The crawled result would appear in travel.json. Each json file has two attributes `url` (indicating what page to show while displaying results) and `text` (we will use this to perform indexing).

