import xmltodict
import json
import pathlib
import time


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


def make_node_dict(hch_id, xml_dict, parent=0):
    # print(xml_dict)
    global node_dict
    node = Node()
    node["OrphaNumber"] = xml_dict["Disorder"]["OrphaNumber"]
    node["name"] = xml_dict["Disorder"]["Name"]
    node["hch_id"] = hch_id
    node["parents"] = [parent]
    # print(node)
    if xml_dict["child"] is not None:
        for child in xml_dict["child"]:
            node["childs"].append(child["Disorder"]["OrphaNumber"])
            make_node_dict(hch_id, child, parent)
    if node["OrphaNumber"] in node_dict:
        node_dict[node["OrphaNumber"]]["childs"] = merge_unique(node_dict[node["OrphaNumber"]]["childs"], node["childs"])
        node_dict[node["OrphaNumber"]]["parents"] = merge_unique(node_dict[node["OrphaNumber"]]["parents"], node["parents"])
        # print(node_dict[node.OrphaNumber].childs)
    else:
        node_dict[node["OrphaNumber"]] = node


def merge_unique(list1, list2):
    for item in list2:
        if item not in list1:
            list1.append(item)
    return list1


def convert(index, hch_id, in_file_path, out_file_path):
    start = time.time()
    global node_dict
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
        make_node_dict(hch_id, child, node["OrphaNumber"])
    node_dict[node["OrphaNumber"]] = node
    print(node_dict)
    print(len(node_dict))

    # Output simplified dictionary
    # with open(out_file_path, "w", encoding="iso-8859-1") as out:
    #     out.write("{{\"index\": {{\"_index\":\"{}\"}}}}\n".format(index))
    #     out.write(json.dumps(xml_dict, indent=2) + "\n")

    # Output elasticsearch injection ready file
    with open(out_file_path, "w", encoding="iso-8859-1") as out:
        for val in node_dict.values():
            out.write("{{\"index\": {{\"_index\":\"{}\"}}}}\n".format(index))
            # out.write(json.dumps(val, indent=2) + "\n")
            out.write(json.dumps(val) + "\n")

    print(time.time() - start, "s")

########################################################################################################################


start = time.time()

in_file_path = pathlib.Path("data_in\\Orphanet_Nomenclature_Pack_EN\\Classification_en\\en\\"
                            "ORPHAclassification_147_Rare_developmental_defect_during_embryogenesis_en.xml")

in_folder = pathlib.Path("data_in\\Orphanet_Nomenclature_Pack_EN\\Classification_en\\en")
out_folder = pathlib.Path("data_out")

index = "classification_orphanet"
target = "folder"

global node_dict
node_dict = {}

if target == "folder":

    for file in in_folder.iterdir():
        node_dict = {}
        file_stem = file.stem
        print(file_stem)
        out_file_name = file_stem + ".json"
        out_file_path = out_folder / out_file_name
        hch_id = file_stem.split("_")[1]
        convert(index, hch_id, file, out_file_path)
        print()
else:
    print()
    print(in_file_path.stem)
    out_file_name = in_file_path.stem + ".json"
    out_file_path = out_folder / out_file_name
    hch_id = in_file_path.split("_")[1]
    convert(index, hch_id, in_file_path, out_file_path)

print()
print(time.time() - start, "s total")
