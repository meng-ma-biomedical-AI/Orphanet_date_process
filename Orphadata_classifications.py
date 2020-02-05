import xmltodict
import json
import pathlib
import time


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
            # curated_dict[]
    elif isinstance(parent, list):
        for elem_list in parent:
            unherit_node_list(elem_list)


def bypass_list(parent, key):
    child_value = parent.pop(key)
    if child_value is not None:
        child_value = [child_value[child] for child in child_value if child][0]
        parent["child"] = child_value
    else:
        parent["child"] = None
    return parent


def convert(in_file_path, out_file_path):
    start = time.time()
    xml_dict = parse_file(in_file_path)
    unherit_node_list(xml_dict)

    with open(out_file_path, "w", encoding="iso-8859-1") as out:
        index_name = "orphadata_classification_146"
        out.write("{{\"index\": {{\"_index\":\"{}\"}}}}\n".format(index_name))
        # out.write(json.dumps(disorder, indent=2) + "\n")
        out.write(json.dumps(xml_dict) + "\n")

    print(time.time() - start, "s")

########################################################################################################################


start = time.time()

in_file_path = pathlib.Path("data_in\\Orphanet_Nomenclature_Pack_EN\\Classification_en\\en\\"
                            "ORPHAclassification_146_Rare_cardiac_disease_en.xml")

out_file_path = pathlib.Path("data_out\\ORPHAclassification_146_Rare_cardiac_disease_en.json")

in_folder = pathlib.Path("data_in\\Orphanet_Nomenclature_Pack_EN\\Classification_en\\en")
out_folder = pathlib.Path("data_out")

target = "folder"

if target == "folder":
    for file in in_folder.iterdir():
        file_stem = file.stem
        print(file_stem)
        out_file_name = file_stem + ".json"
        out_file_path = out_folder / out_file_name
        convert(file, out_file_path)
        print()
else:
    print()
    print(in_file_path.stem)
    convert(in_file_path, out_file_path)

print()
print(time.time() - start, "s total")
