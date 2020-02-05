import xmltodict
import json
import pathlib

in_file_path = pathlib.Path("data_in\\en_product1.xml")
out_file_path = pathlib.Path("data_out\\en_product1.json")


with open(in_file_path, "r", encoding="iso-8859-1") as ini:
    file_dict = xmltodict.parse(ini.read(), xml_attribs=False)

with open(out_file_path, "w", encoding="iso-8859-1") as out:
    for disorder in file_dict["JDBOR"]["DisorderList"]["Disorder"]:
        out.write("{\"index\": {\"_index\":\"product1\"}}" + "\n")
        # out.write(json.dumps(disorder, indent=2) + "\n")
        out.write(json.dumps(disorder) + "\n")

