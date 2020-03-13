import copy
import re

import xmltodict
import json
import pathlib
import time

from elasticsearch import Elasticsearch

from xml.dom import minidom


def parse_file(in_file_path):
    """
    :param in_file_path: path, source xml file
    :return: xml_dict: xml source file parsed as a dictionary
    """
    start = time.time()
    dom1 = minidom.parse(str(in_file_path.resolve()))
    print(dom1.encoding)
    #
    with open(in_file_path, "r", encoding=dom1.encoding) as ini:
    # with open(in_file_path, "r", encoding="iso-8859-1") as ini:
        file_dict = xmltodict.parse(ini.read(), xml_attribs=False)
    xml_dict = file_dict["JDBOR"]["DisorderList"]
    # print(xml_dict)
    xml_dict = json.loads(json.dumps(xml_dict, ensure_ascii=False))
    print("parsing:", time.time() - start)
    return xml_dict


def simplify_xml_list(xml_dict):
    """
    Recursively simplify the xml structure for homogeneity
    Remove
    <ClassificationNodeList count="XX">
        <ClassificationNode>
            <ClassificationNodeChildList count="XX">
    To produce
    ClassificationNode: [{..., ClassificationNodeChild: {}}, ...]

    :param xml_dict: xml source file parsed as a dictionary
    :return: simplified xml_dict
    """
    if isinstance(xml_dict, dict):
        for key, elem in xml_dict.items():
            if key.endswith("List"):
                # print(xml_dict)
                xml_dict = simplify_list(xml_dict, key)
                # print()
            simplify_xml_list(elem)
    elif isinstance(xml_dict, list):
        for elem_list in xml_dict:
            simplify_xml_list(elem_list)
    return xml_dict


def simplify_list(parent, key):
    """
    Remove trivial key and regroup it's children as a "child" property of the trivial key's parent
    Properly map empty children as 'None'

    :param parent: Dictionary containing key to simplify
    :param key: Dictionary key containing the term "*List"
    :return: simplified dictionary
    """
    # child_value = parent.pop(key)
    child_value = parent[key]
    if child_value is not None and child_value != "0":
        # print(child_value)
        child_value = [child_value[child] for child in child_value if child][0]
        # print(child_value)
        if isinstance(child_value, dict) or isinstance(child_value, str):
            child_value = [child_value]
            # print(child_value)
        parent[key] = child_value
    else:
        parent[key] = None
    return parent


def merge_unique(list1, list2):
    """
    Merge two list and keep unique values
    """
    for item in list2:
        if item not in list1:
            list1.append(item)
    return list1


def simplify(xml_dict):
    """
    :param xml_dict: xml source file parsed as a dictionary
    :return: node_list: List of Disorder object with simplified structure
    i.e.:
    [{
        "name": "Congenital pericardium anomaly",
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
    xml_dict = simplify_xml_list(xml_dict)

    # print(xml_dict)
    # output_simplified_dictionary(out_file_path, index, xml_dict)

    node_list = xml_dict["Disorder"]
    node_list = json.dumps(node_list, ensure_ascii=False)

    pattern = re.compile("List\":")
    node_list = pattern.sub("\":", node_list)
    node_list = json.loads(node_list)

    print(len(node_list))
    print("conversion:", time.time() - start, "s")
    return node_list


def recursive_template(elem):
    if isinstance(elem, dict):
        for child in elem:
            recursive_template(child)
    elif isinstance(elem, list):
        for sub_elem in elem:
            recursive_template(sub_elem)
    return elem


def recursive_unwanted_orphacode(elem):
    if isinstance(elem, dict):
        if "OrphaNumber" in elem.keys():
            elem.pop("OrphaNumber")
        for child in elem:
            recursive_unwanted_orphacode(elem[child])
    elif isinstance(elem, list):
        for sub_elem in elem:
            recursive_unwanted_orphacode(sub_elem)
    return elem


def remove_unwanted_orphacode(node_list):
    # print(node_list)
    # TODO: keep disorder Orphanumber
    # Node is a disorder object
    for node in node_list:
        # elem is an attribute of the disorder
        for elem in node:
            recursive_unwanted_orphacode(node[elem])
        # print()
    return node_list


def clean_textual_info(node_list):
    # for each disorder object in the file
    for disorder in node_list:
        TextAuto = ""
        textual_information_list = []
        if "TextAuto" in disorder:
            temp = {}
            TextAuto = disorder["TextAuto"]["Info"]
            temp["Info"] = TextAuto
            textual_information_list.append(temp)
            disorder.pop("TextAuto")
        if "TextualInformation" in disorder:
            if disorder["TextualInformation"] is not None:
                for text in disorder["TextualInformation"]:
                    if text["TextSection"] is not None:
                        temp = {}
                        key = text["TextSection"][0]["TextSectionType"]["Name"]
                        temp[key] = text["TextSection"][0]["Contents"]
                        textual_information_list.append(temp)
            if textual_information_list:
                disorder["TextualInformation"] = textual_information_list
            else:
                disorder["TextualInformation"] = None
        else:
            disorder["TextualInformation"] = None
    return node_list


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
        out.write(json.dumps(xml_dict, indent=2, ensure_ascii=False) + "\n")


def output_elasticsearch_file(out_file_path, index, node_list):
    """
    Output json file, elasticsearch injection ready

    :param out_file_path: path to output file
    :param index: name of the elasticsearch index
    :param node_list: list of Disorder, each will form an elasticsearch document
    :return: None
    """
    start = time.time()
    with open(out_file_path, "w", encoding="UTF-8") as out:
        for val in node_list:
            out.write("{{\"index\": {{\"_index\":\"{}\"}}}}\n".format(index))
            out.write(json.dumps(val, indent=2, ensure_ascii=False) + "\n")
            # out.write(json.dumps(val, ensure_ascii=False) + "\n")
    print("writing:", time.time() - start)


def upload_es(elastic, out_file_path):
    start = time.time()
    full_file = out_file_path.read_text(encoding="UTF-8")
    elastic.bulk(body=full_file)
    print("upload ES:", time.time() - start, "s")


def process(in_file_path, out_folder, elastic):
    file_stem = in_file_path.stem
    index = file_stem
    print(file_stem)
    out_file_name = file_stem + ".json"
    out_file_path = out_folder / out_file_name

    # Parse source xml file
    xml_dict = parse_file(in_file_path)

    node_list = simplify(xml_dict)

    node_list = remove_unwanted_orphacode(node_list)

    node_list = clean_textual_info(node_list)

    output_elasticsearch_file(out_file_path, index, node_list)
    print()

    if elastic:
        # Upload to elasticsearch node
        upload_es(elastic, out_file_path)
        print()

########################################################################################################################


start = time.time()

in_file_path = pathlib.Path("data_in\\data_xml\\Disorders cross referenced with other nomenclatures\\en_product1.xml")

in_folder = pathlib.Path("data_in\\data_xml\\Disorders cross referenced with other nomenclatures")

out_folder = pathlib.Path("data_out")

# Process all input folder or single input file ?
parse_folder = False

upload = False

if upload:
    elastic = Elasticsearch(hosts=["localhost"])
else:
    elastic = False
print()

if parse_folder:
    # Process files in designated folder
    for file in in_folder.iterdir():
        process(file, out_folder, elastic)

else:
    # Process single file
    process(in_file_path, out_folder, elastic)


# print("Example query for 1 disorder in 1 classification")
# print("http://localhost:9200/classification_orphanet/_search?q=OrphaNumber:558%20AND%20hch_id:147")
print(time.time() - start, "s total")
