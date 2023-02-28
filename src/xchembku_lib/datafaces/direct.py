import logging

from xchembku_api.databases.constants import CrystalWellFieldnames, Tablenames

# Base class for generic things.
from xchembku_api.thing import Thing

# Database manager.
from xchembku_lib.databases.databases import Databases

logger = logging.getLogger(__name__)

thing_type = "xchembku_lib.xchembku_datafaces.direct"


class Direct(Thing):
    """ """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None):
        Thing.__init__(self, thing_type, specification)

        self.__database = None

    # ----------------------------------------------------------------------------------------
    async def start(self):
        # Connect to the database to create the schemas if they don't exist already.
        await self.establish_database_connection()

    # ----------------------------------------------------------------------------------------
    async def disconnect(self):
        if self.__database is not None:
            await self.__database.disconnect()
            self.__database = None

    # ----------------------------------------------------------------------------------------
    async def establish_database_connection(self):

        if self.__database is None:
            self.__database = Databases().build_object(self.specification()["database"])
            await self.__database.connect()

    # ----------------------------------------------------------------------------------------
    async def reinstance(self):
        """"""
        if self.__database is None:
            return

        self.__database = self.__database.reinstance()

        return self

    # ----------------------------------------------------------------------------------------
    async def backup(self):
        """"""
        await self.establish_database_connection()

        return await self.__database.backup()

    # ----------------------------------------------------------------------------------------
    async def restore(self, nth):
        """"""
        await self.establish_database_connection()

        return await self.__database.restore(nth)

    # ----------------------------------------------------------------------------------------
    async def query(self, sql, subs=None, why=None):
        """"""
        await self.establish_database_connection()

        records = await self.__database.query(sql, subs=subs, why=why)

        return records

    # ----------------------------------------------------------------------------------------
    async def execute(self, sql, subs=None, why=None):
        """"""
        await self.establish_database_connection()

        return await self.__database.execute(sql, subs=subs, why=why)

    # ----------------------------------------------------------------------------------------
    async def insert(self, table_name, records, why=None):
        """"""
        await self.establish_database_connection()

        return await self.__database.insert(table_name, records, why=why)

    # ----------------------------------------------------------------------------------------
    async def update(self, table_name, record, where, subs=None, why=None):
        """"""
        await self.establish_database_connection()

        if why is None:
            why = f"update {table_name} record"

        # This returns the count of records changed by the update.
        return {
            "count": await self.__database.update(
                table_name, record, where, subs=subs, why=why
            )
        }

    # ----------------------------------------------------------------------------------------
    async def originate_crystal_wells(self, records):
        """
        Caller provides the records containing fields to be created.
        The filename field should be unique in all records.
        """

        table_name = Tablenames.CRYSTAL_WELLS

        return await self.insert(table_name, records, why="originate_crystal_wells")

    # ----------------------------------------------------------------------------------------
    async def update_crystal_wells(self, records, why=None):
        """
        Caller provides the crystal well record with the fields to be updated.
        """

        table_name = Tablenames.CRYSTAL_WELLS

        for record in records:
            result = await self.update(
                table_name,
                record,
                f"({CrystalWellFieldnames.AUTOID} = ?)",
                subs=[record[CrystalWellFieldnames.AUTOID]],
                why=why,
            )

        return result

    # ----------------------------------------------------------------------------------------
    async def fetch_crystal_wells_filenames(self, why=None):
        """
        Caller provides the filters for selecting which crystal wells.
        Returns records from the database.
        """

        table_name = Tablenames.CRYSTAL_WELLS

        if why is None:
            why = "API fetch_crystal_wells_filenames"
        result = await self.query(
            f"SELECT * FROM {table_name}",
            why=why,
        )

        return result

    # ----------------------------------------------------------------------------------------
    async def report_health(self):
        """"""

        report = {}

        report["alive"] = True

        return report

    # ----------------------------------------------------------------------------------------
    async def close_client_session(self):
        """"""

        await self.disconnect()
