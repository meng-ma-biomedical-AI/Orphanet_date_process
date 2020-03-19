import copy
import re

import xmltodict
import json
import pathlib
import time

from elasticsearch import Elasticsearch

import serialize_orphadata


class Node(dict):
    def __init__(self):
        super().__init__()
        self["name"] = ""
        self["OrphaNumber"] = ""
        self["hch_id"] = ""
        self["parents"] = []
        self["childs"] = []


def simplify_node_list(xml_dict):
    """
    Recursively simplify the xml structure for homogeneity
    Remove
    <ClassificationNodeList count="XX">
        <ClassificationNode>
            <ClassificationNodeChildList count="XX">
    To produce
    Child: [{}, ...]

    :param xml_dict: xml source file parsed as a dictionary
    :return: simplified xml_dict
    """
    if isinstance(xml_dict, dict):
        for key, elem in xml_dict.items():
            if key.endswith("List"):
                # print(xml_dict)
                xml_dict = simplify_list(xml_dict, key)
                # print()
            simplify_node_list(elem)
    elif isinstance(xml_dict, list):
        for elem_list in xml_dict:
            simplify_node_list(elem_list)
    return xml_dict


def simplify_list(parent, key):
    """
    Remove trivial key and regroup it's children as a "child" property of the trivial key's parent
    Properly map empty children as 'None'

    :param parent: Dictionary containing key to simplify
    :param key: Dictionary key containing the term "*List"
    :return: simplified dictionary
    """
    child_value = parent.pop(key)
    if child_value is not None:
        # print(child_value)
        child_value = [child_value[child] for child in child_value if child][0]
        # print(child_value)
        if isinstance(child_value, dict):
            child_value = [child_value]
            # print(child_value)
        parent["child"] = child_value
    else:
        parent["child"] = None
    return parent


def make_node_dict(node_dict, hch_id, xml_dict, parent):
    """
    Recursively parse xml_dict to output a collection of Disorder with all their children

    :param node_dict: Dictionary of Disorders i.e.
    {2846: {
        "name": "Congenital pericardium anomaly",
        "OrphaNumber": "2846",
        "hch_id": "148",
        "parents": ["97965"],
        "childs": ["99129", "99130", "99131"]
        },
    2847: {...}
    }
    :param hch_id: String, Orphanet classification number
    :param xml_dict: xml source file parsed as a dictionary
    :param parent: Orpha_ID of parent Disorder
    :return: node_dict
    """
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
            node_dict = make_node_dict(node_dict, hch_id, child, node["OrphaNumber"])
    if node["OrphaNumber"] in node_dict:
        node_dict[node["OrphaNumber"]]["childs"] = merge_unique(node_dict[node["OrphaNumber"]]["childs"], node["childs"])
        node_dict[node["OrphaNumber"]]["parents"] = merge_unique(node_dict[node["OrphaNumber"]]["parents"], node["parents"])
        # print(node_dict[node.OrphaNumber].childs)
    else:
        node_dict[node["OrphaNumber"]] = node
    return node_dict


def merge_unique(list1, list2):
    """
    Merge two list and keep unique values
    """
    for item in list2:
        if item not in list1:
            list1.append(item)
    return list1


def convert(hch_id, xml_dict, rename_orpha):
    """
    :param hch_id: String, Orphanet classification number
    :param xml_dict: xml source file parsed as a dictionary
    :param rename_orpha: boolean, change label OrphaNumber to ORPHAcode
    :return: node_list: List collection of Disorder
    i.e.:
    [
    {"name": "Congenital pericardium anomaly",
    "OrphaNumber": "2846",
    "hch_id": "148",
    "parents": ["97965"],
    "childs": ["99129", "99130", "99131"]
    },
    {...}
    ]
    """
    start = time.time()

    # Simplify the xml structure for homogeneity
    xml_dict = simplify_node_list(xml_dict)

    # Simplify special case for classification root
    try:
        xml_dict["child"] = xml_dict["Disorder"]["child"][0]["child"]
        xml_dict["Disorder"].pop("child")
    except TypeError:
        xml_dict["child"] = None
    # print(xml_dict)

    node_dict = {}
    node = Node()
    node["OrphaNumber"] = xml_dict["Disorder"]["OrphaNumber"]
    node["name"] = xml_dict["Disorder"]["Name"]
    node["hch_id"] = hch_id

    if xml_dict["child"] is not None:
        for child in xml_dict["child"]:
            node["childs"].append(child["Disorder"]["OrphaNumber"])
            node_dict = make_node_dict(node_dict, hch_id, child, node["OrphaNumber"])

    node_dict[node["OrphaNumber"]] = node

    node_list = list(node_dict.values())

    if rename_orpha:
        node_list = json.dumps(node_list, ensure_ascii=False)
        pattern = re.compile("OrphaNumber")
        node_list = pattern.sub("ORPHAcode", node_list)
        node_list = json.loads(node_list)

    # print(node_list)
    print(len(node_list))

    print(time.time() - start, "s")
    return node_list


def process_classification(in_file_path, out_folder, elastic, indent_output):
    """
    Complete Orphadata XML to Elasticsearch JSON process

    :param in_file_path: input file path
    :param out_folder: output folder path
    :param elastic: URI to elastic node, False otherwise
    :param indent_output: indent output file (True for visual data control, MUST be False for elasticsearch upload)
    :return: None (Write file (mandatory) / upload to elastic cluster)
    """

    start = time.time()

    file_stem = in_file_path.stem
    index = file_stem
    print(file_stem)
    out_file_name = file_stem + ".json"
    out_file_path = out_folder / out_file_name

    hch_id = file_stem.split("_")[2]

    # Parse source xml file
    xml_dict = serialize_orphadata.parse_file(in_file_path)

    start = time.time()
    # remove intermediary dictionary (xml conversion artifact) and rename OrphaNumber
    rename_orpha = True  # OrphaNumber to ORPHAcode

    # Output this simplified dictionnary for debug purpose
    node_list = convert(hch_id, xml_dict, rename_orpha)

    print("convert:", time.time() - start, "s")

    # Output/upload function
    serialize_orphadata.output_process(out_file_path, index, node_list, elastic, indent_output)
