import pathlib


# Single file input
import elasticsearch

in_file_path = pathlib.Path("..\\data\\data_RDcode\\Orphanet_Nomenclature_Pack_EN\\en\\ORPHAclassification_146_Rare_cardiac_disease_en.xml")

# List of path to folder containing data
folders = list()

####### API Orphadata ########
# Product 1 cross-reference
# folders.append(pathlib.Path("..\\data\\Orphadata_2021_04\\Rare diseases and classifications\\Cross-referencing of rare diseases\\XML"))

# Product 3 Classifications
# pat_hch_path = pathlib.Path("data_in\\PatHch.Txt")
# folders.append(pathlib.Path("..\\data\\Orphadata_2021_04\\Rare diseases and classifications\\Classifications of rare diseases"))

# Product 4 HPO, phenotype
# folders.append(pathlib.Path("..\\data\\Orphadata_2021_04\\Rare diseases with associated phenotypes"))

# Product 6 Disorder => Gene, (output also Gene => Disorder)
# folders.append(pathlib.Path("..\\data\\Orphadata_2021_04\\Genes associated with rare diseases"))

# Product 9
# folders.append(pathlib.Path("..\\data\\Orphadata_2021_04\\Epidemiological data\\Rare disease epidemiology"))
# folders.append(pathlib.Path("..\\data\\Orphadata_2021_04\\Epidemiological data\\Rare diseases natural history"))
##############################

####### RDcode ########
# RDcode /!\ remember to change index_prefix
# folders.append(pathlib.Path("..\\data\\RDcode_2020\\Orphanet_Nomenclature_Pack_EN"))
# folders.append(pathlib.Path("..\\data\\RDcode_2020\\Orphanet_Nomenclature_Pack_EN\\en"))
# folders.append(pathlib.Path("..\\data\\RDcode_2020\\Orphanet_Nomenclature_Pack_FR"))
# folders.append(pathlib.Path("..\\data\\RDcode_2020\\Orphanet_Nomenclature_Pack_FR\\fr"))

for lang in ["CS", "DE", "EN", "ES", "FR", "IT", "NL", "PL", "PT"]:
    folders.append(pathlib.Path("..\\data\\RDcode_2020\\Orphanet_Nomenclature_Pack_{}".format(lang)))
    folders.append(pathlib.Path("..\\data\\RDcode_2020\\Orphanet_Nomenclature_Pack_{}\\{}".format(lang, lang.lower())))
#########################

out_folder = pathlib.Path("data_out")

# Process all input folders or single input file ?
parse_folder = True

# input encoding: "auto" or valid encoding ("UTF-8" or "iso-8859-1")
input_encoding = "auto"

# ###################################################### OUTPUT ########################################################

# The prefix MUST be 'rdcode' for RDcode API (lowercase index name is mandatory)
# Empty string or False otherwise
index_prefix = "rdcode"

# Remap number as integer
cast_as_integer = True

# Indent output file (True for visual data control, need to be False for elasticsearch upload)
indent_output = False

# Upload to elasticsearch node
upload = True
elastic_node = elasticsearch.Elasticsearch(hosts=["localhost"])

# Make the yaml schema description
make_schema = False

output_encoding = "UTF-8"
