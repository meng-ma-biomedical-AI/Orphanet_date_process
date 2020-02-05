#!/usr/bin/env python3
import xmltodict

import tools
import time
import json
import pathlib
from elasticsearch import Elasticsearch
import auto_index_elastic

"""
This module find the most complete elastic search mapping in order to index a set of file
The process upload each file in a local elastic node, query the mapping and keep the 
biggest ~= (wished to be the most complete)
"""


def auto_index(elastic, in_file_path, out_path, best_index=""):
    with open(in_file_path, "r") as ini:
        best_index_bytes = best_index.encode()
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


def parse_xml(in_file_path):
    with open(in_file_path, "r") as ini:
        xml_dict = xmltodict.parse(ini.read(), xml_attribs=False)
    return xml_dict


########################################################################################################################
start = time.time()

in_file_path = pathlib.Path("data_in\\orphapackets.json")

out_file_path = pathlib.Path("./index.json")

in_folder = pathlib.Path("data_in\\Orphanet_Nomenclature_Pack_EN\\Classification_en\\en")

target = "folder"
elastic = Elasticsearch(hosts=["localhost"])
best_index = ""

if target == "folder":
    all_json = []
    for file in in_folder.iterdir():
        file_stem = file.stem
        print(file_stem)
        if file.suffix == ".xml":
            json_file = json.dumps(parse_xml(file))
        elif file.suffix == ".json":
            json_file = json.load(file)
        else:
            exit(1)
        print(json_file)
        all_json.append(json_file)

    tmp_out_file = pathlib.Path("./tmp.json")
    with open(tmp_out_file, "w") as out:
        for json_file in all_json:
            print(json_file)
            out.write(json_file + "\n")
    best_index = auto_index(elastic, tmp_out_file, out_file_path, best_index)
    print(best_index)
    print()
else:
    print()
    print(in_file_path.stem)
    if in_file_path.suffix == ".xml":
        json_file = json.dumps(parse_xml(in_file_path))
    elif in_file_path.suffix == ".json":
        json_file = json.load(in_file_path)
    else:
        exit(1)
    best_index = auto_index(elastic, json_file, out_file_path, best_index)

print()
print(time.time() - start, "s total")

