import logging

# Fieldnames common to all databases.
from dls_normsql.constants import CommonFieldnames

# Base class for table definitions.
from dls_normsql.table_definition import TableDefinition

from xchembku_api.models.crystal_plate_model import CrystalPlateModel
from xchembku_api.models.crystal_well_autolocation_model import (
    CrystalWellAutolocationModel,
)
from xchembku_api.models.crystal_well_droplocation_model import (
    CrystalWellDroplocationModel,
)
from xchembku_api.models.crystal_well_model import CrystalWellModel

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class CrystalPlatesTable(TableDefinition):
    # ----------------------------------------------------------------------------------------
    def __init__(self):
        model_class = CrystalPlateModel
        table_name = "crystal_plates"

        TableDefinition.__init__(self, table_name)

        fields = model_class.__fields__
        for field_name, field in fields.items():
            field_type = field.type_

            if field_name == "uuid":
                # All images have a unique autoid field.
                self.fields[CommonFieldnames.UUID] = {
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

        # Add indexes.
        self.fields["formulatrix__plate__id"]["index"] = True
        self.fields["barcode"]["index"] = True
        self.fields["visit"]["index"] = True
        self.fields[CommonFieldnames.CREATED_ON]["index"] = True


# ----------------------------------------------------------------------------------------
class CrystalWellsTable(TableDefinition):
    # ----------------------------------------------------------------------------------------
    def __init__(self):
        model_class = CrystalWellModel
        table_name = "crystal_wells"

        TableDefinition.__init__(self, table_name)

        fields = model_class.__fields__
        for field_name, field in fields.items():
            field_type = field.type_

            if field_name == "uuid":
                # All images have a unique autoid field.
                self.fields[CommonFieldnames.UUID] = {
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

        # Add indexes.
        self.fields[CommonFieldnames.CREATED_ON]["index"] = True


# ----------------------------------------------------------------------------------------
class CrystalWellAutolocationsTable(TableDefinition):
    # ----------------------------------------------------------------------------------------
    def __init__(self):
        model_class = CrystalWellAutolocationModel
        table_name = "crystal_well_autolocations"

        TableDefinition.__init__(self, table_name)

        fields = model_class.__fields__
        for field_name, field in fields.items():
            field_type = field.type_

            if field_name == "uuid":
                # All images have a unique autoid field.
                self.fields[CommonFieldnames.UUID] = {
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

        # Remove attribute of the model that doesn't get stored in the database.
        self.fields.pop("crystal_coordinates")

        # Add indexes.
        self.fields["crystal_well_uuid"]["index"] = True
        self.fields[CommonFieldnames.CREATED_ON]["index"] = True


# ----------------------------------------------------------------------------------------
class CrystalWellDroplocationsTable(TableDefinition):
    # ----------------------------------------------------------------------------------------
    def __init__(self):
        model_class = CrystalWellDroplocationModel
        table_name = "crystal_well_droplocations"

        TableDefinition.__init__(self, table_name)

        fields = model_class.__fields__
        for field_name, field in fields.items():
            field_type = field.type_

            if field_name == "uuid":
                # All images have a unique dropid field.
                self.fields[CommonFieldnames.UUID] = {
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

        # Add indexes.
        self.fields["crystal_well_uuid"]["index"] = True
        self.fields[CommonFieldnames.CREATED_ON]["index"] = True
