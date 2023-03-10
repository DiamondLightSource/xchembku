import logging
from typing import Dict, List, Union

from xchembku_api.databases.constants import CrystalWellFieldnames, Tablenames
from xchembku_api.models.well_model import WellModel

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
    async def insert(self, table_name, records, why=None) -> None:
        """"""
        await self.establish_database_connection()

        return await self.__database.insert(table_name, records, why=why)

    # ----------------------------------------------------------------------------------------
    async def update(self, table_name, record, where, subs=None, why=None) -> Dict:
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
    async def originate_crystal_wells(
        self, records: Union[List[Dict], List[WellModel]]
    ) -> None:
        """
        Caller provides the records containing fields to be created.
        The filename field should be unique in all records.
        """

        if len(records) > 0:
            # If we're being given models, serialize them into dicts.
            if isinstance(records[0], WellModel):
                models: List[WellModel] = records
                records = [model.dict() for model in models]

            return await self.insert(
                WellModel.__name__.lower(), records, why="originate_crystal_wells"
            )

    # ----------------------------------------------------------------------------------------
    async def update_crystal_wells(
        self, records: Union[List[Dict], List[WellModel]], why=None
    ) -> Dict:
        """
        Caller provides the crystal well record with the fields to be updated.
        """

        count = 0
        if len(records) > 0:
            # If we're being given models, serialize them into dicts.
            if isinstance(records[0], WellModel):
                models: List[WellModel] = records
                records = [model.dict() for model in models]

            for record in records:
                result = await self.update(
                    WellModel.__name__.lower(),
                    record,
                    f"({CrystalWellFieldnames.AUTOID} = ?)",
                    subs=[record[CrystalWellFieldnames.AUTOID]],
                    why=why,
                )
                count += result.get("count", 0)

        return {"count": count}

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
