# orphadata_elastic

Ver: june 2020

Author: Cyril Bigot


## Purpose
Convert JDBOR extract (xml files such as product1-9,
nomenclature and classification) to elasticsearch files ready for injection.

Transformation process include:
* Regroup definitions in product1 or RDcode orphanomenclature (see clean_textual_info)
* transform single key object to value (see clean_single_name_object)
* rename some terms (see rename_terms in each module)

Can also produce the corresponding yaml scheme for API contract definition.

## Requirements
| package | ver |
| --- | --- |
| python | 3.8 |
| elasticsearch | 7.6.0 |
| xmltodict | 0.12.0 |

## Usage

Download manually the Orphadata xml or use some scripts
from download_new_orpha.bat (only working from copy/paste command line)

Settings: [config_orphadata_elastic.py](./config_orphadata_elastic.py)

launch [orphadata_elastic.py](./orphadata_elastic.py) to convert
the Orphadata xml to json format, elastic ready

[yaml_schema_descriptor.py](./yaml_schema_descriptor.py) can be launched 
separately to convert the previously generated json to yaml schema for
OpenAPI definition
