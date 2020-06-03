#!/usr/bin/env python3

import json
from elasticsearch import Elasticsearch

# mapping dictionary that contains the settings and
# _mapping schema for a new Elasticsearch index:
demo_mapping = {
    "settings": {
        "number_of_shards": 2,
        "number_of_replicas": 1
    },
    "mappings": {
        "properties": {
            "some_string": {
                "type": "text"  # formerly "string"
            },
            "some_bool": {
                "type": "boolean"
            },
            "some_int": {
                "type": "integer"
            },
            "some_more_text": {
                "type": "text"
            }
        }
    }
}

"""
Demo module to create and get an elasticsearch mapping with the external elasticsearch module
"""


def clear_test_mapping(elastic):
    elastic.indices.delete(index="tmp_index", ignore=[400, 404])


def get_mapping(elastic, index="tmp_index"):
    tmp_indice = elastic.indices.get_mapping(index)
    return tmp_indice


def create_mapping(elastic, mapping):
    response = elastic.indices.create(
        index="tmp_index",
        body=mapping,
        ignore=400  # ignore 400 already exists code
    )
    detailed_response = ""
    if 'acknowledged' in response:
        if response['acknowledged']:
            detailed_response = "\nINDEX MAPPING SUCCESS FOR INDEX: {}\n".format(response['index'])

    # catch API error response
    elif 'error' in response:
        err = "\nERROR: {}\n".format(response['error']['root_cause'])
        err_type = "TYPE: {}\n".format(response['error']['type'])
        detailed_response = err + err_type
    # print out the response:
    detailed_response = detailed_response + "response: {}\n".format(response)
    return detailed_response


def bulk_data(elastic, json_line):
    complete_line = "{\"index\": {}}" + "\n" + json.dumps(json_line)
    response = elastic.bulk(complete_line, index="tmp_index")
    return response


if __name__ == "__main__":
    elastic = Elasticsearch(hosts=["localhost"])
    clear_test_mapping(elastic)
    print(create_mapping(elastic, demo_mapping))
    print(get_mapping(elastic))
