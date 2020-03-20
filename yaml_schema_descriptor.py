import pathlib
import json
import time

from config_serialize_orphadata import *


def input_type(data, encoding):
    if isinstance(data, type(pathlib.Path())):
        # print("Path as input")
        # parse the file keep the first element
        with open(data, "r", encoding=encoding) as ini:
            for line in ini:
                # skip index declaration
                if not line.startswith("{\"index\": {\"_index\":"):
                    data = json.loads(line)
                    if None in data:
                        pass
                    else:
                        break
    return data


def recursive_format_schema(data, main_indent):
    prop_list = list()
    for key, value in data.items():
        # print(key)
        if isinstance(value, str):
            prop = '{}{}:\n'.format(main_indent, key) + \
                   '{}  type: string\n'.format(main_indent) + \
                   '{}  example: \"{}\"\n'.format(main_indent, value)
            prop_list.append(prop)

        elif isinstance(value, dict):
            prop = '{}{}:\n'.format(main_indent, key) + \
                   '{}  type: array\n'.format(main_indent) + \
                   '{}  items:\n'.format(main_indent) + \
                   '{}    type: string\n'.format(main_indent) + \
                   '{}    example: {}\n'.format(main_indent, [x for x in value])
            prop_list.append(prop)

            indent = main_indent + "    "
            prop = recursive_format_schema(value, indent)
            prop_list.append("".join(prop))

        elif isinstance(value, list):
            if len(value) > 0:
                prop = '{}{}:\n'.format(main_indent, key) + \
                       '{}  type: array\n'.format(main_indent) + \
                       '{}  items:\n'.format(main_indent) + \
                       '{}    type: string\n'.format(main_indent) + \
                       '{}    example: {}\n'.format(main_indent, [x for x in value[0:2]])
                prop_list.append(prop)

                indent = main_indent + "    "

                if isinstance(value[0], dict):
                    prop = recursive_format_schema(value[0], indent)
                    prop_list.append("".join(prop))

    prop_list = "".join(prop_list)

    return prop_list


def format_schema(data):
    main_indent = " " * 4

    text = 'disorder:\n' \
           '  type: object\n' \
           '  properties:\n'

    var_text = recursive_format_schema(data, main_indent)

    required = '  required:\n    - ORPHAcode'

    schema = text + var_text + required
    return schema


def output_schema(out_file_path, schema):
    with open(out_file_path, "w", encoding="UTF-8") as out:
        out.write(schema)


def yaml_schema(out_folder, in_file_path, output_encoding):
    start = time.time()
    data = input_type(in_file_path, output_encoding)
    # print(data)
    schema = format_schema(data)

    out_file_path = pathlib.Path(str(out_folder) + "\\schema\\" +
                                 str(in_file_path.stem) + ".yaml")

    output_schema(out_file_path, schema)
    print("yaml_schema", time.time() - start, "s")


if __name__ == "__main__":
    in_file_path = pathlib.Path("data_out\\produit6 gene\\new_product6_04032020_gene.json")

    yaml_schema(out_folder, in_file_path, output_encoding)
