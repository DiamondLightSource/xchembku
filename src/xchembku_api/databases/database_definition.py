import logging

# All the tables.
from xchembku_api.databases.table_definitions import (
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

        self.LATEST_REVISION = 5

    # ----------------------------------------------------------------------------------------
    async def apply_revision(self, database, revision):

        logger.debug(f"applying revision {revision}")

        if revision == 3:

            # Add crytal plate formulatrix__experiment__name field and index.
            await database.execute(
                "ALTER TABLE crystal_plates ADD COLUMN formulatrix__experiment__name TEXT",
                why=f"revision {revision}: new column",
            )
            await database.execute(
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
            await database.execute(
                "ALTER TABLE crystal_well_droplocations ADD COLUMN is_exported_to_soakdb3 BOOLEAN",
                why="revision {revision}: new column",
            )
            await database.execute(
                "CREATE INDEX %s_%s ON %s(%s)"
                % (
                    "crystal_well_droplocations",
                    "is_exported_to_soakdb3",
                    "crystal_well_droplocations",
                    "is_exported_to_soakdb3",
                )
            )

        if revision == 5:
            # Add crytal plate error field.
            await database.execute(
                "ALTER TABLE crystal_plates ADD COLUMN error TEXT",
                why="revision {revision}: new column",
            )

    # ----------------------------------------------------------------------------------------
    async def add_table_definitions(self, database):
        """
        Make all the table definitions.
        """

        # Table schemas in our database.
        database.add_table_definition(CrystalPlatesTable())
        database.add_table_definition(CrystalWellsTable())
        database.add_table_definition(CrystalWellAutolocationsTable())
        database.add_table_definition(CrystalWellDroplocationsTable())
