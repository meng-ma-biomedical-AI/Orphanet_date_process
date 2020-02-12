import xmltodict
import json
import pathlib
import time

from elasticsearch import Elasticsearch


class Node(dict):
    def __init__(self):
        self["name"] = ""
        self["OrphaNumber"] = ""
        self["hch_id"] = ""
        self["parents"] = []
        self["childs"] = []


def parse_file(in_file_path):
    with open(in_file_path, "r", encoding="iso-8859-1") as ini:
        file_dict = xmltodict.parse(ini.read(), xml_attribs=False)
    xml_dict = file_dict["JDBOR"]["DisorderList"]
    return xml_dict


def unherit_node_list(parent):
    if isinstance(parent, dict):
        for key, elem in parent.items():
            if key.endswith("List"):
                parent = bypass_list(parent, key)
                # print(elem)
            # print(elem)
            unherit_node_list(elem)
    elif isinstance(parent, list):
        for elem_list in parent:
            unherit_node_list(elem_list)


def bypass_list(parent, key):
    child_value = parent.pop(key)
    if child_value is not None:
        child_value = [child_value[child] for child in child_value if child][0]
        if isinstance(child_value, dict):
            child_value = [child_value]
            # print(child_value)
        parent["child"] = child_value
    else:
        parent["child"] = None
    return parent


def make_node_dict(node_dict, hch_id, xml_dict, parent=0):
    # print(xml_dict)
    node = Node()
    node["OrphaNumber"] = xml_dict["Disorder"]["OrphaNumber"]
    node["name"] = xml_dict["Disorder"]["Name"]
    node["hch_id"] = hch_id
    node["parents"] = [parent]
    # print(node)
    if xml_dict["child"] is not None:
        for child in xml_dict["child"]:
            node["childs"].append(child["Disorder"]["OrphaNumber"])
            node_dict = make_node_dict(node_dict, hch_id, child, parent)
    if node["OrphaNumber"] in node_dict:
        node_dict[node["OrphaNumber"]]["childs"] = merge_unique(node_dict[node["OrphaNumber"]]["childs"], node["childs"])
        node_dict[node["OrphaNumber"]]["parents"] = merge_unique(node_dict[node["OrphaNumber"]]["parents"], node["parents"])
        # print(node_dict[node.OrphaNumber].childs)
    else:
        node_dict[node["OrphaNumber"]] = node
    return node_dict


def merge_unique(list1, list2):
    for item in list2:
        if item not in list1:
            list1.append(item)
    return list1


def convert(node_dict, hch_id, in_file_path):
    start = time.time()
    xml_dict = parse_file(in_file_path)
    unherit_node_list(xml_dict)
    xml_dict["child"] = xml_dict["Disorder"]["child"][0]["child"]
    xml_dict["Disorder"].pop("child")

    # print(xml_dict)
    node = Node()
    node["OrphaNumber"] = xml_dict["Disorder"]["OrphaNumber"]
    node["name"] = xml_dict["Disorder"]["Name"]
    node["hch_id"] = hch_id
    for child in xml_dict["child"]:
        node["childs"].append(child["Disorder"]["OrphaNumber"])
        make_node_dict(node_dict, hch_id, child, node["OrphaNumber"])
    node_dict[node["OrphaNumber"]] = node
    print(node_dict)
    print(len(node_dict))

    print(time.time() - start, "s")
    return node_dict


def output_simplified_dictionary(out_file_path, index, xml_dict):
    # Output simplified dictionary
    with open(out_file_path, "w", encoding="iso-8859-1") as out:
        out.write("{{\"index\": {{\"_index\":\"{}\"}}}}\n".format(index))
        out.write(json.dumps(xml_dict, indent=2) + "\n")


def output_elasticsearch_file(out_file_path, index, node_dict):
    # Output elasticsearch injection ready file
    with open(out_file_path, "w", encoding="iso-8859-1") as out:
        for val in node_dict.values():
            out.write("{{\"index\": {{\"_index\":\"{}\"}}}}\n".format(index))
            # out.write(json.dumps(val, indent=2) + "\n")
            out.write(json.dumps(val) + "\n")

########################################################################################################################


start = time.time()

in_file_path = pathlib.Path("data_in\\Orphanet_Nomenclature_Pack_EN\\Classification_en\\en\\"
                            "ORPHAclassification_147_Rare_developmental_defect_during_embryogenesis_en.xml")

in_folder = pathlib.Path("data_in\\Orphanet_Nomenclature_Pack_EN\\Classification_en\\en")
out_folder = pathlib.Path("data_out")

index = "classification_orphanet"
target = "folder"

elastic = Elasticsearch(hosts=["localhost"])

if target == "folder":
    # Process folder
    for file in in_folder.iterdir():
        node_dict = {}

        file_stem = file.stem
        print(file_stem)
        out_file_name = file_stem + ".json"
        out_file_path = out_folder / out_file_name

        hch_id = file_stem.split("_")[1]
        node_dict = convert(node_dict, hch_id, file)
        output_elasticsearch_file(out_file_path, index, node_dict)
        print()

        # Upload to elasticsearch node
        # full_file = out_file_path.read_text(encoding="iso-8859-1")
        # elastic.bulk(body=full_file)
else:
    # Process single file
    node_dict = {}
    print()

    file_stem = in_file_path.stem
    print(file_stem)
    out_file_name = file_stem + ".json"
    out_file_path = out_folder / out_file_name

    hch_id = file_stem.split("_")[1]
    convert(node_dict, hch_id, in_file_path)
    output_elasticsearch_file(out_file_path, index, node_dict)
    print()

    # Upload to elasticsearch node
    full_file = out_file_path.read_text(encoding="iso-8859-1")
    elastic.bulk(body=full_file)

print()
print(time.time() - start, "s total")
