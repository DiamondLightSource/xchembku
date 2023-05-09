import logging

# All the tables.
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

        self.LATEST_REVISION = 4

    # ----------------------------------------------------------------------------------------
    async def apply_revision(self, revision):

        logger.debug(f"applying revision {revision}")

        if revision == 3:

            # Add crytal plate formulatrix__experiment__name field and index.
            await self.execute(
                "ALTER TABLE crystal_plates ADD COLUMN formulatrix__experiment__name TEXT",
                why=f"revision {revision}: new column",
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

        if revision == 4:
            # Add crytal plate formulatrix__experiment__name field and index.
            await self.execute(
                "ALTER TABLE crystal_well_droplocations ADD COLUMN is_exported_to_soakdb3 BOOLEAN",
                why="revision {revision}: new column",
            )
            await self.execute(
                "CREATE INDEX %s_%s ON %s(%s)"
                % (
                    "crystal_well_droplocations",
                    "is_exported_to_soakdb3",
                    "crystal_well_droplocations",
                    "is_exported_to_soakdb3",
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
