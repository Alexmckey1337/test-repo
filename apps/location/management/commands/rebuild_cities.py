from datetime import datetime

from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from apps.location.models import City, District

es = Elasticsearch(['es'])


class Command(BaseCommand):
    def set_data(self, cities, index_name='city', doc_type_name='doc'):
        districts = {d['id']: {'name': d['name'], 'english': d['english']}
                     for d in District.objects.values('id', 'name', 'english')}
        cities = cities.iterator(chunk_size=10000)
        for c in cities:
            body = {
                'pk': c.id,
                'name': c.name,
                'english': c.english,
                'level': c.level,
                'vid': c.vid,
                'added': datetime.now(),
                'timezone': c.timezone,
                'area': {
                    'id': c.area.id,
                    'name': c.area.name,
                    'english': c.area.english,
                    'country': {
                        'id': c.area.country_id,
                        'name': c.area.country.name,
                        'fullname': c.area.country.fullname,
                        'english': c.area.country.english,
                    },
                },
                'country': {
                    'id': c.country_id,
                    'name': c.country.name,
                    'fullname': c.country.fullname,
                    'english': c.country.english,
                },
            }
            lat = c.latitude
            lon = c.longitude
            if lat and lon:
                body['location'] = {'lat': lat, 'lon': lon}
            district = districts.get(c.rajon)
            if district:
                body['district'] = {
                    'id': c.rajon,
                    'name': district['name'],
                    'english': district['english'],
                }
            yield {
                '_index': index_name,
                '_type': doc_type_name,
                '_id': c.id,
                '_source': body,
            }

    def set_mapping(self, es, index_name="city", doc_type_name="doc"):
        country = {
            "properties": {
                "id": {
                    "type": "keyword",
                    "ignore_above": 3
                },
                "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "english": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "fullname": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
            }
        }
        area = {
            "properties": {
                "id": {
                    "type": "long"
                },
                "english": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "country": country,
            }
        }
        district = {
            "properties": {
                "id": {
                    "type": "long"
                },
                "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "english": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
            }
        }
        my_mapping = {
            "doc": {
                "properties": {
                    "pk": {
                        "type": "long"
                    },
                    "name": {
                        "type": "text"
                    },
                    "english": {
                        "type": "text"
                    },
                    "level": {
                        "type": "integer"
                    },
                    "vid": {
                        "type": "integer"
                    },
                    "timezone": {
                        "type": "float"
                    },
                    "location": {
                        "type": "geo_point"
                    },
                    "added": {
                        "type": "date"
                    },
                    "area": area,
                    "country": country,
                    "district": district,
                }
            }
        }
        es.indices.delete(index=index_name, ignore_unavailable=True)
        create_index = es.indices.create(index=index_name, body={
            'settings': {'number_of_shards': 1},
            'mappings': my_mapping,
        })
        mapping_index = es.indices.put_mapping(index=index_name, doc_type=doc_type_name, body=my_mapping)
        if create_index["acknowledged"] != True or mapping_index["acknowledged"] != True:
            self.stdout.write("Index creation failed...")

    def handle(self, *args, **options):
        self.stdout.write('Start...')
        self.set_mapping(es)
        self.stdout.write('Mapping complete')
        cities = City.objects.select_related('country', 'area__country')
        try:
            success, _ = bulk(es, self.set_data(cities))
        except Exception as err:
            self.stdout.write(str(err))

        self.stdout.write(
            'Successfully updated %s cities\n' % cities.count())
