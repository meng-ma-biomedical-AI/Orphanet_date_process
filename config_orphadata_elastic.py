import pathlib

import elasticsearch

in_file_path = None
in_file_path = pathlib.Path("data_inputs/en_product1.xml")
# in_file_path = pathlib.Path("..\\data\\data_RDcode\\Orphanet_Nomenclature_Pack_EN\\en\\ORPHAclassification_146_Rare_cardiac_disease_en.xml")


parse_folder = True if not in_file_path else False # Process all input folders or single input file ?
folders = [pathlib.Path('data_inputs')]  # List of path to folder containing data
# for lang in ["CS", "DE", "EN", "ES", "FR", "IT", "NL", "PL", "PT"]:
#     folders.append(pathlib.Path("..\\data\\RDcode_2020\\Orphanet_Nomenclature_Pack_{}".format(lang)))
#     folders.append(pathlib.Path("..\\data\\RDcode_2020\\Orphanet_Nomenclature_Pack_{}\\{}".format(lang, lang.lower())))

out_folder = pathlib.Path("data_out")
input_encoding = "auto"  # input encoding: "auto" or valid encoding ("UTF-8" or "iso-8859-1")
index_prefix = ""  # Empty string or False otherwise - The prefix MUST be 'rdcode' for RDcode API (lowercase index name is mandatory)
cast_as_integer = True  # Remap number as integer
indent_output = False  # Indent output file (True for visual data control, need to be False for elasticsearch upload)
upload = True  # Upload to elasticsearch node if true
elastic_node = elasticsearch.Elasticsearch(hosts=["localhost"], timeout=20)  #  load elastic node
make_schema = False  # Make the yaml schema description
output_encoding = "UTF-8"

PRODUCT_DEF = {
    "product1": "Rare diseases and alignment with terminologies and databases",
    "product3": "Clinical classifications of rare diseases",
    "product4": "Phenotypes associated with rare diseases",
    "product6": "Genes associated with rare diseases",
    "product7": "Linearisation of rare diseases",
    "product9": "Epidemiological data associated with rare diseases",
}






####### Data content for Orphadata API ########
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

####### Data content for RDcode API ########
# RDcode /!\ remember to change index_prefix
# folders.append(pathlib.Path("..\\data\\RDcode_2020\\Orphanet_Nomenclature_Pack_EN"))
# folders.append(pathlib.Path("..\\data\\RDcode_2020\\Orphanet_Nomenclature_Pack_EN\\en"))
# folders.append(pathlib.Path("..\\data\\RDcode_2020\\Orphanet_Nomenclature_Pack_FR"))
# folders.append(pathlib.Path("..\\data\\RDcode_2020\\Orphanet_Nomenclature_Pack_FR\\fr"))

#########################