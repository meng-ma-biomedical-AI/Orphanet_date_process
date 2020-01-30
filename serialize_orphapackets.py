#!/usr/bin/env python3

import tools
import time
import json
import pathlib
from elasticsearch import Elasticsearch
import auto_index_elastic


def find_all_keys(json_line, key_list):
    print("################################")
    # print("key_list:", key_list)
    for list_item in json_line["ORPHApacket"]:
        # print("key:", list_item)
        if isinstance(list_item, dict):
            print("will append key:", list_item)
            key_list.append(list_item)
    return key_list


def auto_index(elastic, file_path, out_path):
    with open(file_path, "r") as ini:
        best_index = ""
        best_index_bytes = "a".encode()
        biggest_size = 0
        for line in ini:
            if not line.startswith("{\"index"):
                json_line = json.loads(line)
                # print(json_line)
                auto_index_elastic.bulk_data(elastic, json_line)
                auto_index = auto_index_elastic.get_mapping(elastic)
                auto_index_bytes = json.dumps(auto_index).encode()

                if auto_index_bytes != best_index_bytes:
                    size_obj = tools.get_size(auto_index)
                    if size_obj.size > biggest_size:
                        best_index = auto_index
                        biggest_size = size_obj.size
                        best_index_bytes = auto_index_bytes
                        print(best_index)
                        print(size_obj.size)
                auto_index_elastic.clear_test_mapping(elastic)

    with open(out_path, "w") as out:
        json.dump(best_index["tmp_index"], out)

    return best_index["tmp_index"]


########################################################################################################################

start_time = time.time()

file_path = pathlib.Path("C:/Users/cbigot/Downloads/orphapackets.json")
# file_path = pathlib.Path("C:/Users/cbigot/Downloads/orphapackets_short.json")
out_path = pathlib.Path("./index.json")

orphapackets = {}
elastic = Elasticsearch(hosts=["localhost"])

best_index = auto_index(elastic, file_path, out_path)
print(best_index)

# print(orphapackets["558"])
# print(json.dumps(orphapackets["558"], indent=4))

print(time.time() - start_time)
