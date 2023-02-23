import logging

# Base class for table definitions.
from dls_normsql.table_definition import TableDefinition

from xchembku_api.databases.constants import CrystalWellFieldnames, Tablenames

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class RockmakerImagesTable(TableDefinition):
    # ----------------------------------------------------------------------------------------
    def __init__(self):
        TableDefinition.__init__(self, Tablenames.CRYSTAL_WELLS)

        # All images have a unique autoid field.
        self.fields[CrystalWellFieldnames.AUTOID] = {
            "type": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "index": True,
        }

        self.fields[CrystalWellFieldnames.FILENAME] = {"type": "TEXT", "index": True}
        self.fields[CrystalWellFieldnames.ERROR] = {"type": "TEXT", "index": False}
        self.fields[CrystalWellFieldnames.WIDTH] = {"type": "INTEGER", "index": False}
        self.fields[CrystalWellFieldnames.HEIGHT] = {"type": "INTEGER", "index": False}
        self.fields[CrystalWellFieldnames.WELL_CENTER_X] = {
            "type": "INTEGER",
            "index": False,
        }
        self.fields[CrystalWellFieldnames.WELL_CENTER_Y] = {
            "type": "INTEGER",
            "index": False,
        }
        self.fields[CrystalWellFieldnames.TARGET_POSITION_X] = {
            "type": "INTEGER",
            "index": False,
        }
        self.fields[CrystalWellFieldnames.TARGET_POSITION_Y] = {
            "type": "INTEGER",
            "index": False,
        }
        self.fields[CrystalWellFieldnames.CRYSTAL_PROBABILITY] = {
            "type": "FLOAT",
            "index": False,
        }
        self.fields[CrystalWellFieldnames.NUMBER_OF_CRYSTALS] = {
            "type": "INTEGER",
            "index": False,
        }
        self.fields[CrystalWellFieldnames.IS_USABLE] = {
            "type": "BOOLEAN",
            "index": False,
        }
        self.fields[CrystalWellFieldnames.IS_DROP] = {"type": "BOOLEAN", "index": False}
        self.fields[CrystalWellFieldnames.CREATED_ON] = {"type": "TEXT", "index": False}
