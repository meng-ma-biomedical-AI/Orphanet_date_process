# orphadata_elastic

Download manually the Orphadata xml or use some scripts
from download_new_orpha.bat
AND download PatHch.Txt from plator for the classification tag

Settings: [config_orphadata_elastic.py](./config_orphadata_elastic.py)

launch [orphadata_elastic.py](./orphadata_elastic.py) to convert
the Orphadata xml to json format, elastic ready

[yaml_schema_descriptor.py](./yaml_schema_descriptor.py) can be launched 
separately to convert the previously generated json to yaml schema for
OpenAPI definition
