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

        if revision == 1:
            await self.execute(
                "ALTER TABLE crystal_plates ADD COLUMN formulatrix__experiment__name TEXT",
                why="revision 2: add crystal_plates.formulatrix__experiment__name column",
            )
            await self.execute(
                "CREATE INDEX %s_%s ON %s(%s)"
                % (
                    "crystal_plates",
                    "formulatrix__experiment__name",
                    "crystal_plates",
                    "formulatrix__experiment__name",
                )
            )

            # Crystal wells didn't get indexed in revision 1.
            await self.execute(
                "CREATE INDEX %s_%s ON %s(%s)"
                % (
                    "crystal_wells",
                    "position",
                    "crystal_wells",
                    "position",
                )
            )

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
