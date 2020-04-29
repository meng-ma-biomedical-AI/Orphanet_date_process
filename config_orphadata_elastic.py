import pathlib


# Single file input
in_file_path = pathlib.Path("data_in\\data_xml\\Orphanet classifications\\en_product3_146.xml")

# List of path to folder containing data
folders = list()

# Product 1 cross-reference
# folders.append(pathlib.Path("data_in\\data_xml\\Disorders cross referenced with other nomenclatures"))

# Product 3 Classifications
# pat_hch_path = pathlib.Path("data_in\\PatHch.Txt")
# folders.append(pathlib.Path("data_in\\data_xml\\Orphanet classifications"))

# Product 4 HPO, phenotype
# folders.append(pathlib.Path("data_in\\data_xml\\Phenotypes associated with rare disorders"))

# Product 6 Disorder => Gene, (output also Gene => Disorder)
# folders.append(pathlib.Path("data_in\\data_xml\\Disorders with their associated genes"))

# Product 9
# folders.append(pathlib.Path("data_in\\data_xml\\Epidemiological data\\Rare disease epidemiology"))
# folders.append(pathlib.Path("data_in\\data_xml\\Epidemiological data\\Natural history"))

# RDcode
folders.append(pathlib.Path("C:\\Users\\Cyrlynx\\PycharmProjects\\data_RDcode\\Orphanet_Nomenclature_Pack_EN"))
folders.append(pathlib.Path("C:\\Users\\Cyrlynx\\PycharmProjects\\data_RDcode\\Orphanet_Nomenclature_Pack_EN\\en"))

out_folder = pathlib.Path("data_out")

# Process all input folders or single input file ?
parse_folder = True

# input encoding: "auto" or valid encoding ("UTF-8" or "iso-8859-1")
input_encoding = "auto"


######################################################## OUTPUT ########################################################

# The prefix MUST be 'rdcode' for RDcode API (lowercase index name is mandatory)
# Empty string or False otherwise
index_prefix = "rdcode"

# Indent output file (True for visual data control, need to be False for elasticsearch upload)
indent_output = False

# Upload to elasticsearch node
upload = True

# Make the yaml schema description
make_schema = False

output_encoding = "UTF-8"
