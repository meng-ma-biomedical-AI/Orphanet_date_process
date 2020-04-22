import copy
import re

import xmltodict
import json
import pathlib
import time

import elasticsearch

import orphadata_classifications
import yaml_schema_descriptor
from config_orphadata_elastic import *


def parse_file(in_file_path, input_encoding):
    """
    :param in_file_path: path, source xml file
    :param input_encoding:
    :return: xml_dict: xml source file parsed as a dictionary
    """
    start = time.time()

    if input_encoding.lower() == "auto":
        with open(in_file_path, "rb") as ini:
            xml_declaration = ini.readline()

        xml_declaration = xml_declaration.decode()
        pattern = re.compile("encoding=\"(.*)\"[ ?]")
        encoding = pattern.search(xml_declaration).group(1)
        print(encoding)

        with open(in_file_path, "r", encoding=encoding) as ini:
            file_dict = xmltodict.parse(ini.read(), xml_attribs=False)

    else:
        with open(in_file_path, "r", encoding=input_encoding) as ini:
            print(input_encoding, "(from config file)")
            file_dict = xmltodict.parse(ini.read(), xml_attribs=False)

    key = list(file_dict["JDBOR"].keys())
    if "Availability" in key:
        key.pop(key.index("Availability"))
    # print(key)
    if len(key) == 1:
        key = key[0]
    else:
        print("ERROR: Multiple root XML key:")
        print(key)
        exit(1)

    xml_dict = file_dict["JDBOR"][key]
    # print(xml_dict)
    # DumpS then loadS: convert ordered dict to dict
    # xml_dict = json.loads(json.dumps(xml_dict, ensure_ascii=False))
    print("parsing:", time.time() - start)
    return xml_dict


def simplify_xml_list(xml_dict):
    """
    Recursively simplify the xml structure for homogeneity
    Remove
    <ClassificationNodeList count="XX">
        <ClassificationNode>
            <ClassificationNodeChildList count="XX">
    To produce
    ClassificationNode: [{..., ClassificationNodeChild: {}}, ...]

    :param xml_dict: xml source file parsed as a dictionary
    :return: simplified xml_dict
    """
    if isinstance(xml_dict, dict):
        for key, elem in xml_dict.items():
            if key.endswith("List"):
                # print(xml_dict)
                xml_dict = simplify_list(xml_dict, key)
                # print()
            simplify_xml_list(elem)
    elif isinstance(xml_dict, list):
        for elem_list in xml_dict:
            simplify_xml_list(elem_list)
    return xml_dict


def simplify_list(parent, key):
    """
    Remove trivial key and regroup it's children as a "child" property of the trivial key's parent
    Properly map empty children as 'None'

    :param parent: Dictionary containing key to simplify
    :param key: Dictionary key containing the term "*List"
    :return: simplified dictionary
    """
    # child_value = parent.pop(key)
    child_value = parent[key]
    if child_value is not None and child_value != "0":
        # print(child_value)
        child_value = [child_value[child] for child in child_value if child][0]
        # print(child_value)
        if isinstance(child_value, dict) or isinstance(child_value, str):
            child_value = [child_value]
            # print(child_value)
        parent[key] = child_value
    else:
        parent[key] = None
    return parent


def merge_unique(list1, list2):
    """
    Merge two list and keep unique values
    """
    for item in list2:
        if item not in list1:
            list1.append(item)
    return list1


def simplify(xml_dict, rename_orpha):
    """
    :param xml_dict: xml source file parsed as a dictionary
    :return: node_list: List of Disorder object with simplified structure
    i.e.:
    [{
        "name": "Congenital pericardium anomaly",
        "ORPHAcode": "2846",
        "hch_id": "148",
        "parents": ["97965"],
        "childs": ["99129", "99130", "99131"]
    },
    {...}
    ]
    """
    start = time.time()

    # Simplify the xml structure for homogeneity
    xml_dict = simplify_xml_list(xml_dict)

    # print(xml_dict)
    # output_simplified_dictionary(out_file_path, index, xml_dict)

    key = list(xml_dict.keys())
    # print(key)
    if len(key) == 1:
        key = key[0]
    else:
        print("ERROR: Multiple disorder level key:")
        print(key)
        exit(1)

    node_list = xml_dict[key]
    node_list = json.dumps(node_list, ensure_ascii=False)

    pattern = re.compile("List\":")
    node_list = pattern.sub("\":", node_list)
    if rename_orpha:
        pattern = re.compile("OrphaNumber")
        node_list = pattern.sub("ORPHAcode", node_list)
    node_list = json.loads(node_list)

    print(len(node_list), "disorder concepts")
    # print("simplify:", time.time() - start, "s")
    return node_list


def recursive_template(elem):
    if isinstance(elem, dict):
        for child in elem:
            recursive_template(child)
    elif isinstance(elem, list):
        for sub_elem in elem:
            recursive_template(sub_elem)
    return elem


def recursive_unwanted_orphacode(elem):
    """
    Remove the ORPHAcode past the one defined at the disorder's root level
    ! NO quality check !
    Useless since new Orphadata generation

    :param elem: disorder object or property
    :return: disorder object or property without ORPHAcode key
    """
    if isinstance(elem, dict):
        if "ORPHAcode" in elem.keys():
            elem.pop("ORPHAcode")
        for child in elem:
            recursive_unwanted_orphacode(elem[child])
    elif isinstance(elem, list):
        for sub_elem in elem:
            recursive_unwanted_orphacode(sub_elem)
    return elem


def remove_unwanted_orphacode(node_list):
    """
    Remove the ORPHAcode past the one defined at the disorder's root level
    ! NO quality check !
    Useless since new Orphadata generation

    :param node_list: list of disorder
    :return: list of disorder without ORPHAcode key past the main one
    """
    # print(node_list)
    for disorder in node_list:
        # elem is an attribute of the disorder
        for elem in disorder:
            recursive_unwanted_orphacode(disorder[elem])
        # print()
    return node_list


def clean_textual_info(node_list):
    """
    For product 1 (cross references)

    :param node_list: list of disorder
    :return: list of disorder with reworked textual info
    """
    # for each disorder object in the file
    for disorder in node_list:
        TextAuto = ""
        textual_information_list = []
        if "TextAuto" in disorder:
            temp = {}
            TextAuto = disorder["TextAuto"]["Info"]
            temp["Info"] = TextAuto
            textual_information_list.append(temp)
            disorder.pop("TextAuto")
        if "TextualInformation" in disorder:
            if disorder["TextualInformation"] is not None:
                for text in disorder["TextualInformation"]:
                    if text["TextSection"] is not None:
                        temp = {}
                        key = text["TextSection"][0]["TextSectionType"]["Name"]
                        temp[key] = text["TextSection"][0]["Contents"]
                        textual_information_list.append(temp)
            if textual_information_list:
                disorder["TextualInformation"] = textual_information_list
            else:
                disorder["TextualInformation"] = None
        else:
            disorder["TextualInformation"] = None
    return node_list


def recursive_clean_single_name_object(elem):
    """
    Take the list of disorder and substitute object by a text if they contain only one "Name" property
    keeps multi-property object otherwise
    i.e.:
    disorder["DisorderType"]["Name"] = "Disease"
    to =>
    disorder["DisorderType"] = "Disease"
    Work in depth recursively
    :param elem: property of disorder
    :return: list of disorder without single name object
    """
    if isinstance(elem, dict):
        keys = elem.keys()
        if len(keys) == 1:
            if "Name" in keys:
                name = elem.pop("Name")
                elem = name
        else:
            for child in elem:
                elem[child] = recursive_clean_single_name_object(elem[child])
    elif isinstance(elem, list):
        for index, sub_elem in enumerate(elem):
            sub_elem = recursive_clean_single_name_object(sub_elem)
            elem[index] = sub_elem
    return elem


def clean_single_name_object(node_list):
    """
    Take the list of disorder and substitute object by a text if they contain only one "Name" property
    keeps multi-property object otherwise
    i.e.:
    disorder["DisorderType"]["Name"] = "Disease"
    to =>
    disorder["DisorderType"] = "Disease"
    Work in depth recursively
    :param node_list: list of disorder
    :return: list of disorder without single name object
    """
    for disorder in node_list:
        for elem in disorder:
            disorder[elem] = recursive_clean_single_name_object(disorder[elem])
    return node_list


def gene_indexing(node_list_gene):
    """
    Invert the indexing of the product6 "gene" to index the relationships between gene and disorder
    from the gene point of view

    :param node_list_gene: copy of processed node_list
    :return: similar list of disorder-gene relation but indexed by gene
    ie.
    [
    {
    "Name": "kinesin family member 7",
    "Symbol": "KIF7",
    "Synonym": [
        "JBTS12"
    ],
    "GeneType": "gene with protein product",
    "ExternalReference": [
        {
        "Source": "Ensembl",
        "Reference": "ENSG00000166813"
        },
        {...},
    ],
    "Locus": [
        {
        "GeneLocus": "15q26.1",
        "LocusKey": "1"
        }
    ],
    "GeneDisorderAssociation": [
        {
        "SourceOfValidation": "22587682[PMID]",
        "DisorderGeneAssociationType": "Disease-causing germline mutation(s) in",
        "DisorderGeneAssociationStatus": "Assessed",
        "disorder": {
            "ORPHAcode": "166024",
            "ExpertLink": "http://www.orpha.net/consor/cgi-bin/OC_Exp.php?lng=en&Expert=166024",
            "Name": "Multiple epiphyseal dysplasia, Al-Gazali type",
            "DisorderType": "Disease",
            "DisorderGroup": "Disorder"
        }
        },
        {...}
    ]
    }
    ]
    """
    gene_dict = dict()
    for disorder in node_list_gene:
        # disorder still contains gene association
        disorder_info = copy.deepcopy(disorder)

        # association_list : list, need to exploit with according gene
        # disorder_info now only contains disorder
        association_list = disorder_info.pop("DisorderGeneAssociation")

        for association_info in association_list:
            # Each association_info contains a different Gene,
            # we need to index the Gene then substitute it with disorder_info
            gene_info = association_info.pop("Gene")
            gene_index = gene_info["Symbol"]
            # Initialize the Gene index on first occurrence
            if gene_index not in gene_dict:
                gene_dict[gene_index] = {}
                for gene_prop, gene_prop_value in gene_info.items():
                    gene_dict[gene_index][gene_prop] = gene_prop_value
                gene_dict[gene_index]["GeneDisorderAssociation"] = []
            # insert disorder_info in the association_info
            association_info["disorder"] = disorder_info
            # Extend the GeneDisorderAssociation with this new disorder relation
            gene_dict[gene_index]["GeneDisorderAssociation"].append(association_info)

    node_list_gene = list(gene_dict.values())
    return node_list_gene


def output_simplified_dictionary(out_file_path, index, xml_dict, indent_output, output_encoding):
    """
    Output simplified dictionary in json format DEBUG helper function

    Simplified the xml structure to give a consistent hierarchy:
    Disorder: {}
    Child: [
        {
        Disorder: {}
        Child: []
        },
        {
        Disorder: {}
        Child: []
        }
    ]

    :param out_file_path: path to output file
    :param index: name of the elasticsearch index
    :param xml_dict: xml source file parsed as a dictionary
    :return: None
    """
    if indent_output:
        indent = 2
    else:
        indent = None
    with open(out_file_path, "w", encoding=output_encoding) as out:
        out.write("{{\"index\": {{\"_index\":\"{}\"}}}}\n".format(index))
        out.write(json.dumps(xml_dict, indent=indent, ensure_ascii=False) + "\n")


def output_elasticsearch_file(out_file_path, index, node_list, indent_output, output_encoding):
    """
    Output json file, elasticsearch injection ready

    :param out_file_path: path to output file
    :param index: name of the elasticsearch index
    :param node_list: list of Disorder, each will form an elasticsearch document
    :param indent_output: if True, will pretty print with indent = 2 ; MUST be false for ES upload or schema description
    :param output_encoding: "UTF-8" or "iso-8859-1"
    :return: None
    """
    start = time.time()
    if indent_output:
        indent = 2
    else:
        indent = None
    with open(out_file_path, "w", encoding=output_encoding) as out:
        for val in node_list:
            out.write("{{\"index\": {{\"_index\":\"{}\"}}}}\n".format(index))
            out.write(json.dumps(val, indent=indent, ensure_ascii=False) + "\n")
    print("writing:", time.time() - start)


def upload_es(elastic, processed_json_file):
    """
    Upload processed json file to elasticsearch node

    :param elastic: URI to elastic node, False otherwise
    :param processed_json_file: path
    :return: None
    """
    start = time.time()
    full_file = processed_json_file.read_text(encoding="UTF-8")
    try:
        elastic.bulk(body=full_file)
    except elasticsearch.exceptions.ConnectionError:
        print("ERROR: elasticsearch node unavailable")
        exit(1)
    print("upload ES:", time.time() - start, "s")


def process(in_file_path, out_folder, elastic, input_encoding, indent_output, output_encoding):
    """
    Complete Orphadata XML to Elasticsearch JSON process

    :param in_file_path: input file path
    :param out_folder: output folder path
    :param elastic: URI to elastic node, False otherwise
    :param input_encoding:
    :param indent_output:
    :param output_encoding:
    :return: None (Write file (mandatory) / upload to elastic cluster)
    """
    file_stem = in_file_path.stem.lower()
    index = file_stem
    print("####################")
    print(file_stem)
    out_file_name = file_stem + ".json"
    out_file_path = out_folder / out_file_name

    # Parse source xml file
    xml_dict = parse_file(in_file_path, input_encoding)

    start = time.time()
    # remove intermediary dictionary (xml conversion artifact) and rename OrphaNumber
    rename_orpha = True  # OrphaNumber to ORPHAcode
    node_list = simplify(xml_dict, rename_orpha)

    # Output this simplified dictionnary for debug purpose
    output_simplified_dictionary(out_file_path, index, node_list, indent_output, output_encoding)

    # Useless since new Orphadata generation
    # Remove orphacode past the main one (/!\ NO QUALITY CHECK)
    # node_list = remove_unwanted_orphacode(node_list)

    # Regroup textual_info for product1
    if "product1" in file_stem:
        node_list = clean_textual_info(node_list)

    # Remap object with single "Name" to string
    node_list = clean_single_name_object(node_list)

    # Index product6 "gene" by gene symbol
    if "product6" in file_stem:
        node_list_gene = copy.deepcopy(node_list)
        node_list_gene = gene_indexing(node_list_gene)
        out_file_path_gene = pathlib.Path(str(out_file_path.absolute()).split(".")[0] + "_gene" + out_file_path.suffix)
        index_gene = out_file_path_gene.stem
        # Output/upload function
        output_process(out_file_path_gene, index_gene, node_list_gene, elastic, indent_output, output_encoding)

    print("convert:", time.time() - start, "s")

    # Output/upload function
    output_process(out_file_path, index, node_list, elastic, indent_output, output_encoding)


def output_process(out_file_path, index, node_list, elastic, indent_output, output_encoding):
    """
    Output processed node list in elasticsearch JSON and eventually upload the file to "elastic" URI

    :param out_file_path: path
    :param index: index name that will be in elasticsearch indexing instruction
    :param node_list: collection of Disorder (Orphanet concept) object
    :param elastic: URI to elastic node, False otherwise
    :param indent_output: Indent output file (True for visual data control, MUST be False for elasticsearch upload)
    :param output_encoding:
    :return: None
    """
    # Output a json elasticsearch ready, with index name as indexing instruction
    output_elasticsearch_file(out_file_path, index, node_list, indent_output, output_encoding)
    print()

    if elastic:
        # Upload to elasticsearch node
        upload_es(elastic, out_file_path)
        print()

    if make_schema:
        if out_file_path.stem.startswith("en"):
            if "product3" in out_file_path.stem:
                if out_file_path.stem.endswith("146"):
                    yaml_schema_descriptor.yaml_schema(out_folder, out_file_path, output_encoding)
            else:
                yaml_schema_descriptor.yaml_schema(out_folder, out_file_path, output_encoding)
            print()

########################################################################################################################


if __name__ == "__main__":
    start = time.time()

    # Some config check
    if indent_output:
        if upload:
            print("ERROR: Bad configuration, should be mutually exclusive:\n"
                  "\tindent_output:", indent_output, "\n\tupload:", upload)
        if make_schema:
            print("ERROR: Bad configuration, should be mutually exclusive:\n"
                  "\tindent_output:", indent_output, "\n\tmake_schema:", make_schema)
        if upload or make_schema:
            exit(1)

    if upload:
        elastic = elasticsearch.Elasticsearch(hosts=["localhost"])
    else:
        elastic = False
    print()

    if parse_folder:
        # Process files in designated folders
        for folder in folders:
            for file in folder.iterdir():
                # Test to remove "product4_HPO_status" from process
                # this line will be deprecated in future Orphadata generation
                if not file.is_dir():
                    if file.suffix == ".xml":
                        if not str(file.stem).endswith("_status"):
                            if "product3" in file.stem:
                                orphadata_classifications.process_classification(file, out_folder, elastic, input_encoding,
                                                                                 indent_output, output_encoding)
                            else:
                                process(file, out_folder, elastic, input_encoding, indent_output, output_encoding)

    else:
        # Process single file
        file = in_file_path
        if "product3" in file.stem:
            orphadata_classifications.process_classification(file, out_folder, elastic, input_encoding,
                                                             indent_output, output_encoding)
        else:
            process(file, out_folder, elastic, input_encoding, indent_output, output_encoding)

    # print("Example query for 1 disorder in 1 classification")
    # print("http://localhost:9200/classification_orphanet/_search?q=ORPHAcode:558%20AND%20hch_id:147")
    print(time.time() - start, "s total")
