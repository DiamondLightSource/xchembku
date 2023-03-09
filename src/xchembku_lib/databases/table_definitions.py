import logging

# Base class for table definitions.
from dls_normsql.table_definition import TableDefinition

from xchembku_api.databases.constants import CrystalWellFieldnames, Tablenames
from xchembku_api.models.well_model import WellModel

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class RockmakerImagesTable(TableDefinition):
    # ----------------------------------------------------------------------------------------
    def __init__(self):
        model_class = WellModel
        table_name = model_class.__name__.lower()

        TableDefinition.__init__(self, table_name)

        fields = model_class.__fields__
        for field_name, field in fields.items():
            field_type = field.type_

            if field_name == "uuid":
                # All images have a unique autoid field.
                self.fields[CrystalWellFieldnames.AUTOID] = {
                    "type": "TEXT PRIMARY KEY",
                    "index": True,
                }

            else:
                if field_type == int:
                    sql_type = "INTEGER"
                elif field_type == str:
                    sql_type = "TEXT"
                elif field_type == float:
                    sql_type = "REAL"
                elif field_type == bool:
                    sql_type = "BOOLEAN"

                self.fields[field_name] = {"type": sql_type}

            # self.fields["filename"]["index"] = True
