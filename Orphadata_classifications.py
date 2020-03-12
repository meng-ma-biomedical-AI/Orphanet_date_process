import xmltodict
import json
import pathlib
import time

from elasticsearch import Elasticsearch


class Node(dict):
    def __init__(self):
        super().__init__()
        self["name"] = ""
        self["OrphaNumber"] = ""
        self["hch_id"] = ""
        self["parents"] = []
        self["childs"] = []


def parse_file(in_file_path):
    """
    :param in_file_path: path, source xml file
    :return: xml_dict: xml source file parsed as a dictionary
    """
    with open(in_file_path, "r", encoding="iso-8859-1") as ini:
        file_dict = xmltodict.parse(ini.read(), xml_attribs=False)
    xml_dict = file_dict["JDBOR"]["DisorderList"]
    return xml_dict


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


def convert(hch_id, in_file_path):
    """
    :param hch_id: String, Orphanet classification number
    :param in_file_path: path, source xml file
    :return: node_dict: Dictionary collection of Disorder
    i.e.:
    {2846: {
        "name": "Congenital pericardium anomaly",
        "OrphaNumber": "2846",
        "hch_id": "148",
        "parents": ["97965"],
        "childs": ["99129", "99130", "99131"]
        },
    2847: {...}
    }
    """
    start = time.time()

    # Parse source xml file
    xml_dict = parse_file(in_file_path)

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

    print(node_dict)
    print(len(node_dict))

    print(time.time() - start, "s")
    return node_dict


def output_simplified_dictionary(out_file_path, index, xml_dict):
    """
    Output simplified dictionary in json format
    Simplified the xml structure to give a consistent hierarchy:
    Disorder: {}
    Child: [
        {
        Disorder: {}
        Child: []
        },
        {
        Disorder: {}
        Child: []
        }
    ]

    :param out_file_path: path to output file
    :param index: name of the elasticsearch index
    :param xml_dict: xml source file parsed as a dictionary
    :return: None
    """
    with open(out_file_path, "w", encoding="UTF-8") as out:
        out.write("{{\"index\": {{\"_index\":\"{}\"}}}}\n".format(index))
        out.write(json.dumps(xml_dict, indent=2) + "\n")


def output_elasticsearch_file(out_file_path, index, node_dict):
    """
    Output json file, elasticsearch injection ready

    :param out_file_path: path to output file
    :param index: name of the elasticsearch index
    :param node_dict: Dictionary collection of Disorder
        i.e.:
        {2846: {
            "name": "Congenital pericardium anomaly",
            "OrphaNumber": "2846",
            "hch_id": "148",
            "parents": ["97965"],
            "childs": ["99129", "99130", "99131"]
            },
        2847: {...}
        }
    :return: None
    """
    with open(out_file_path, "w", encoding="UTF-8") as out:
        for val in node_dict.values():
            out.write("{{\"index\": {{\"_index\":\"{}\"}}}}\n".format(index))
            # out.write(json.dumps(val, indent=2) + "\n")
            out.write(json.dumps(val) + "\n")


def upload_es(elastic, out_file_path):
    full_file = out_file_path.read_text(encoding="UTF-8")
    elastic.bulk(body=full_file)

########################################################################################################################


start = time.time()

in_file_path = pathlib.Path("data_in\data_xml\Orphanet classifications")

in_folder = pathlib.Path("data_in\data_xml\Orphanet classifications")

out_folder = pathlib.Path("data_out")

index = "classification_orphanet"

# Process all input folder or single input file ?
parse_folder = True

upload = False

if upload:
    elastic = Elasticsearch(hosts=["localhost"])

print()

if parse_folder:
    # Process files in designated folder
    for file in in_folder.iterdir():

        file_stem = file.stem
        print(file_stem)
        out_file_name = file_stem + ".json"
        out_file_path = out_folder / out_file_name

        # String, Orphanet classification number
        hch_id = file_stem.split("_")[2]

        node_dict = convert(hch_id, file)
        output_elasticsearch_file(out_file_path, index, node_dict)
        print()

        if upload:
            # Upload to elasticsearch node
            upload_es(elastic, out_file_path)

else:
    # Process single file

    file_stem = in_file_path.stem
    print(file_stem)
    out_file_name = file_stem + ".json"
    out_file_path = out_folder / out_file_name

    # String, Orphanet classification number
    hch_id = file_stem.split("_")[2]

    node_dict = convert(hch_id, in_file_path)
    output_elasticsearch_file(out_file_path, index, node_dict)
    print()

    if upload:
        # Upload to elasticsearch node
        upload_es(elastic, out_file_path)

print("Example query for 1 disorder in 1 classification")
print("http://localhost:9200/classification_orphanet/_search?q=OrphaNumber:558%20AND%20hch_id:147")
print(time.time() - start, "s total")
