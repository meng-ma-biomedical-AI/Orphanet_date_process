#!/usr/bin/env python3

import json
import pathlib
from elasticsearch import Elasticsearch
import auto_index_elastic

file_path = pathlib.Path("C:/Users/cbigot/Downloads/orphapackets.json")

orphapackets = {}

# print(orphapackets["558"])
# print(json.dumps(orphapackets["558"], indent=4))


def find_all_keys(json_line, key_list):
    print("################################")
    # print("key_list:", key_list)
    for list_item in json_line["ORPHApacket"]:
        # print("key:", list_item)
        if isinstance(list_item, dict):
            print("will append key:", list_item)
            key_list.append(list_item)
    return key_list


def auto_index(elastic, mapping):
    auto_index_elastic.clear_test_mapping(elastic)
    print(auto_index_elastic.create_mapping(elastic, mapping))
    # print(auto_index_elastic.get_mapping(elastic))


########################################################################################################################

elastic = Elasticsearch(hosts=["localhost"])


with open(file_path, "r") as ini:
    key_list = []
    for line in ini:
        if not line.startswith("{\"index"):
            json_line = json.loads(line)
            print(json_line)
            # orphapackets[json_line["ORPHApacketID"]] = json_line["ORPHApacket"]
            # key_list = find_all_keys(json_line, key_list)
            auto_index(elastic, demo_mapping)
            exit()
    print(key_list)
