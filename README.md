# Travel Search
**Information Retrieval Class Project - Group #4**

A complete search engine, optimized for travel, built using Python 3 by the talented developers below

#### Authors
|         Section |        Developer        | GitHub                                         |
|----------------:|:-----------------------:|------------------------------------------------|
|        Crawling |    Prajjwal Bhargava    | [@prajjwal1](https://github.com/prajjwal1)     |
|        Indexing |       Brian Nguyen      | [@briannoogin](https://github.com/briannoogin) |
|       Interface |        Caleb Hoff       | [@CrunchyCat](https://github.com/CrunchyCat)   |
|      Clustering |        Autumn Pin       | [@pin-a](https://github.com/pin-a)             |
| Query Expansion | Swamynathan Singaravelu | [@ssMD16](https://github.com/ssMD16)           |

#### Installing Dependencies
```
$ pip3 install -r requirements.txt
```

## 1. Crawling
> Maintainer: [@prajjwal1](https://github.com/prajjwal1)

```
$ cd crawl
$ scrapy crawl travel -O travel.json
```
The crawled result would appear in travel.json. Each json file has two attributes `url` (indicating what page to show while displaying results) and `text` (we will use this to perform indexing).

## 2. Indexing
> Maintainer: [@briannoogin](https://github.com/briannoogin)

After web pages are crawled, they are indexed and the links they contain are analyzed.

## 3. Interface
> Maintainer: [@CrunchyCat](https://github.com/CrunchyCat) 

```
$ cd travelsearch
$ python app.py
```
The interface is made using Flask and is displayed in a web browser.

## 4. Clustering
> Maintainer: [@pin-a](https://github.com/pin-a)

Web pages are clustered and used to improve the relevance of search results.

## 5. Query Expansion
> Maintainer: [@ssMD16](https://github.com/ssMD16)

Query Expansion is used to provide relevant results to the user.
