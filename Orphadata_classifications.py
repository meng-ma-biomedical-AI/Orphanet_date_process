import xmltodict
import json
import pathlib

in_file_path = pathlib.Path("data_in\\ORPHAclassification_146_Rare_cardiac_disease_en.xml")
out_file_path = pathlib.Path("data_out\\ORPHAclassification_146_Rare_cardiac_disease_en.json")


with open(in_file_path, "r", encoding="iso-8859-1") as ini:
    file_dict = xmltodict.parse(ini.read(), xml_attribs=False)

# print(json.dumps(file_dict["JDBOR"]["DisorderList"], indent=2))

xml_dict = file_dict["JDBOR"]["DisorderList"]

curated_dict = {}


def unherit_node_list(xml_dict):
    if isinstance(xml_dict, dict):
        for key, elem in xml_dict.items():
            # print(elem)
            unherit_node_list(elem)
    elif isinstance(xml_dict, list):
        for elem_list in xml_dict:
            unherit_node_list(elem_list)
    else:
        print(xml_dict)
        pass


########################################################################################################################


unherit_node_list(xml_dict)

exit()
with open(out_file_path, "w", encoding="iso-8859-1") as out:
    out.write("{\"index\": {\"_index\":\"product1\"}}" + "\n")
    # out.write(json.dumps(disorder, indent=2) + "\n")
    out.write(json.dumps(xml_dict) + "\n")

