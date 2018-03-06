from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch

es = Elasticsearch(['es'])


class Command(BaseCommand):
    def set_mapping(self, es, index_name="request", doc_type_name="doc"):
        my_mapping = {
            "doc": {
                "properties": {
                    "duration": {
                        "type": "float"
                    },
                    "user_agent": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "host": {
                        "type": "keyword"
                    },
                    "referer": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "path": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "method": {
                        "type": "keyword"
                    },
                    "query_string": {
                        "type": "text"
                    },
                    "status_code": {
                        "type": "integer"
                    },
                    'user': {
                        'properties': {
                            'name': {
                                "type": "text"
                            },
                            'id': {
                                "type": "long"
                            }
                        }
                    },
                    'real_user': {
                        'properties': {
                            'name': {
                                "type": "text"
                            },
                            'id': {
                                "type": "long"
                            }
                        }
                    },
                    "timestamp": {
                        "type": "date"
                    },
                }
            }
        }
        # es.indices.delete(index=index_name, ignore_unavailable=True)
        create_index = es.indices.create(index=index_name, body={
            'settings': {
                'number_of_shards': 1,
            },
            'mappings': my_mapping,
        })
        mapping_index = es.indices.put_mapping(index=index_name, doc_type=doc_type_name, body=my_mapping)
        if create_index["acknowledged"] or mapping_index["acknowledged"]:
            self.stdout.write("Index creation failed...")

    def handle(self, *args, **options):
        self.stdout.write('Start...')
        self.set_mapping(es)
        self.stdout.write('Mapping complete')
