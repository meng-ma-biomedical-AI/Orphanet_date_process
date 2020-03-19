import pathlib


# Single file input
in_file_path = pathlib.Path("data_in\\data_xml\\Orphanet classifications\\en_product3_146.xml")

# List of path to folder containing data
folders = list()

# Product 1
# folders.append(pathlib.Path("data_in\\data_xml\\Disorders cross referenced with other nomenclatures"))

# Product 3
# folders.append(pathlib.Path("data_in\\data_xml\\Orphanet classifications"))

# Product 4
# folders.append(pathlib.Path("data_in\\data_xml\\Phenotypes associated with rare disorders"))

# Product 6
folders.append(pathlib.Path("data_in\\data_xml\\Disorders with their associated genes"))

# Product 9
# folders.append(pathlib.Path("data_in\\data_xml\\Epidemiological data\\Rare disease epidemiology"))
# folders.append(pathlib.Path("data_in\\data_xml\\Epidemiological data\\Natural history"))

out_folder = pathlib.Path("data_out")

# Process all input folders or single input file ?
parse_folder = False

# Upload to elasticsearch node
upload = False

# auto or valid encoding: "UTF-8" or "iso-5589-1"
input_encoding = "auto"