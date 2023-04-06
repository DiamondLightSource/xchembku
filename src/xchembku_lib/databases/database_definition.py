import logging

# Base class for all aiosqlite database objects.
from xchembku_lib.databases.table_definitions import (
    CrystalPlatesTable,
    CrystalWellAutolocationsTable,
    CrystalWellDroplocationsTable,
    CrystalWellsTable,
)

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class DatabaseDefinition:
    """
    Class which defines the database tables and revision migration path.
    Used in concert with the normsql class.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self):
        """
        Construct object.  Do not connect to database.
        """

        self.LATEST_REVISION = 2

    # ----------------------------------------------------------------------------------------
    async def apply_revision(self, revision):
        pass

        # from xchembku_api.databases.constants import Tablenames
        # from xchembku_api.databases.constants import CrystalWellFieldnames
        # if revision == 2:
        #     await self.execute(
        #         f"ALTER TABLE {Tablenames.CRYSTAL_WELLS} ADD COLUMN {CrystalWellFieldnames.NEWFIELD} TEXT",
        #         why=f"revision 2: add {Tablenames.CRYSTAL_WELLS} {CrystalWellFieldnames.NEWFIELD} column",
        #     )
        #     await self.execute(
        #         "CREATE INDEX %s_%s ON %s(%s)"
        #         % (
        #             Tablenames.CRYSTAL_WELLS,
        #             CrystalWellFieldnames.NEWFIELD,
        #             Tablenames.CRYSTAL_WELLS,
        #             CrystalWellFieldnames.NEWFIELD,
        #         )
        #     )

    # ----------------------------------------------------------------------------------------
    async def add_table_definitions(self):
        """
        Make all the table definitions.
        """

        # Table schemas in our database.
        self.add_table_definition(CrystalPlatesTable())
        self.add_table_definition(CrystalWellsTable())
        self.add_table_definition(CrystalWellAutolocationsTable())
        self.add_table_definition(CrystalWellDroplocationsTable())
