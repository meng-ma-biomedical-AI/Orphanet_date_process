#!/usr/bin/env python3

from elasticsearch import Elasticsearch
# or: elastic = Elasticsearch(hosts=["localhost"])

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

# make some API call to the Elasticsearch cluster


def clear_test_mapping(elastic_node):
    elastic_node.indices.delete(index="tmp_index", ignore=[400, 404])


def get_mapping(elastic_node):
    tmp_indice = elastic_node.indices.get_mapping("tmp_index")
    return tmp_indice


def create_mapping(elastic_node, mapping):
    response = elastic_node.indices.create(
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


if __name__ == "__main__":
    elastic_node = Elasticsearch(hosts=["localhost"])
    clear_test_mapping(elastic_node)
    print(create_mapping(elastic_node, demo_mapping))
    print(get_mapping(elastic_node))
