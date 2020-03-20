import pathlib
import json
from config_serialize_orphadata import *


def input_type(data, encoding="UTF-8"):
    if isinstance(data, type(pathlib.Path())):
        print("Path as input")
        # it's a path, parse the file
        with open(data, "r", encoding=encoding) as ini:
            for line in ini:
                # skip index declaration
                if not line.startswith("{\"index\": {\"_index\":"):
                    data = json.loads(line)
                    if None in data:
                        pass
                    else:
                        break

    elif isinstance(data, list()):
        print("Serialize_orphadata as input")
        data = data[0]

    return data


def format_schema(data):
    text = 'disorder:\n' \
           '  type: object\n' \
           '  properties:\n' \
           '    ORPHAcode:\n' \
           '      type: string\n' \
           '      example: "558"\n'
    prop_list = list()
    # main_indent = " " * 4
    indent = " " * 4
    for key, value in data.items():
        skip = False
        print(key)
        if key == "ORPHAcode":
            skip = True
        elif isinstance(value, str):
            prop = '{}{}:\n'.format(indent, key) + \
                   '{}  type: string\n'.format(indent) + \
                   '{}  example: {}\n'.format(indent, value)
        elif isinstance(value, list):
            prop = '{}{}:\n'.format(indent, key) + \
                   '{}  type: array\n'.format(indent) + \
                   '{}  items:\n'.format(indent) + \
                   '{}    type: string\n'.format(indent) + \
                   '{}    example: {}\n'.format(indent, [x for x in value[0:2]])
        elif isinstance(value, dict):
            print("DICT")

        if not skip:
            prop_list.append(prop)

    prop_list.append('  required:\n    - ORPHAcode')
    vartext = "".join(prop_list)
    schema = text + vartext
    return schema


def output_schema(out_file_path, schema):
    with open(out_file_path, "w", encoding="UTF-8") as out:
        out.write(schema)
    pass


def yaml_schema(out_file_path, data):
    data = input_type(data)
    print(data)
    schema = format_schema(data)
    output_schema(out_file_path, schema)


data = pathlib.Path("data_out\\produit6 gene\\new_product6_04032020.json")

out_file_path = out_folder / "schema" / "en_product3_146.yaml"

# out_file_path = pathlib.Path("data_out\\schema\\en_product3_146.yaml")

yaml_schema(out_file_path, data)
