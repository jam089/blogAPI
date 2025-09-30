from core import settings

article = {
    "title": {
        "type": "text",
        "analyzer": "russian",
    },
    "text": {
        "type": "text",
        "analyzer": "russian",
    },
    "topic": {
        "type": "text",
        "analyzer": "russian",
    },
    "author_name": {
        "type": "text",
        "analyzer": "russian",
    },
}


index_dict = {settings.es.articles_index: article}
