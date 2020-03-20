import pathlib
import json

data = pathlib.Path("data_out\\produit3 classification\\en_product3_146.json")


def input_type(data, encoding="UTF-8"):
    if isinstance(data, type(pathlib.Path())):
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
        data = data[0]

    return data


def format_schema(data):
    schema = data
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

out_file_path =

yaml_schema(out_file_path, data)