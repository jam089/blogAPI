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

fields_weight = ["title^3", "text", "topic^2", "author_name^1.5"]

index_dict = {settings.es.articles_index: article}
