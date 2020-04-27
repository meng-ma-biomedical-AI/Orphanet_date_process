import json
import re


def clean_textual_info_RDcode(node_list, file_stem):
    """
    For product 1 (cross references)

    :param node_list: list of disorder
    :param file_stem: name of file without extension
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
                        key = "Definition"
                        temp[key] = text["TextSection"][0]["Contents"]
                        textual_information_list.append(temp)
            if textual_information_list:
                disorder["Definition"] = textual_information_list[0]["Definition"]
                disorder.pop("TextualInformation")
            else:
                disorder["Definition"] = "None available"
        else:
            disorder["Definition"] = "None available"
    return node_list


def insert_date(node_list, extract_date):
    """
    Append the JDBOR extract date to each disorder entry

    :param node_list: list of disorder objects
    :param extract_date: JDBOR extract date
    :return: node_list with extract date
    """
    for node in node_list:
        node["Date"] = extract_date
    return node_list


def rename_terms(node_list, file_stem):
    """
    Rename some terms for RDcode

    :param node_list: list of disorder objects
    :param file_stem: file name without extension
    :return: node_list with renamed terms
    """
    node_list = json.dumps(node_list)

    patterns = {"\"Totalstatus\":": "\"Status\":",
                "\"Name\":": "\"Preferred term\":",
                "\"PreferredTerm\":": "\"Preferred term\":",
                "\"GroupOfType\":": "\"GroupType\":",
                "\"ExpertLink\":": "\"OrphanetURL\":",
                "\"DisorderType\":": "\"Type\":",
                "\"ExternalReference\":": "\"Code ICD\":",
                "\"Reference\":": "\"Code ICD10\":",
                }

    for key, value in patterns.items():
        pattern = re.compile(key)
        node_list = pattern.sub(value, node_list)

    node_list = json.loads(node_list)
    return node_list


def rework_ICD(node_list):
    """
    remove "source" from ICD external reference

    :param node_list:
    :return: node_list with reworked ICD reference
    """
    for node in node_list:
        if node["Code ICD"]:
            for index, ref in enumerate(node["Code ICD"]):
                node["Code ICD"][index].pop("Source")
    return node_list
