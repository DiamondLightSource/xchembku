import logging
from typing import Dict, List, Optional, Union

from dls_normsql.constants import CommonFieldnames
from dls_utilpack.callsign import callsign
from dls_utilpack.describe import describe

# Base class for generic things.
from dls_utilpack.thing import Thing

from xchembku_api.models.crystal_well_autolocation_model import (
    CrystalWellAutolocationModel,
)
from xchembku_api.models.crystal_well_droplocation_model import (
    CrystalWellDroplocationModel,
)
from xchembku_api.models.crystal_well_filter_model import CrystalWellFilterModel
from xchembku_api.models.crystal_well_model import CrystalWellModel
from xchembku_api.models.crystal_well_needing_droplocation_model import (
    CrystalWellNeedingDroplocationModel,
)

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
        # TODO: Consider if direct dataface needs a start method.
        await self.establish_database_connection()

    # ----------------------------------------------------------------------------------------
    async def disconnect(self):
        if self.__database is not None:
            logger.debug(f"{callsign(self)} disconnecting")
            await self.__database.disconnect()
            logger.debug(f"{callsign(self)} disconnected")
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
    async def originate_crystal_wells_serialized(self, records: List[Dict]) -> None:
        # We are being given json, so parse it into models.
        models = [CrystalWellModel(**record) for record in records]
        # Return the method doing the work.
        return await self.originate_crystal_wells(models)

    # ----------------------------------------------------------------------------------------
    async def originate_crystal_wells(self, models: List[CrystalWellModel]) -> None:
        """
        Caller provides the records containing fields to be created.
        The filename field should be unique in all records.
        """

        # We're being given models, so serialize them into dicts to give to the sql.
        records = [model.dict() for model in models]

        return await self.insert(
            "crystal_wells",
            records,
            why="originate_crystal_wells",
        )

    # ----------------------------------------------------------------------------------------
    async def update_crystal_wells_serialized(self, records: List[Dict]) -> Dict:
        # We are being given json, so parse it into models.
        models = [CrystalWellModel(**record) for record in records]
        # Return the method doing the work.
        return await self.update_crystal_wells(models)

    # ----------------------------------------------------------------------------------------
    async def update_crystal_wells(
        self, models: List[CrystalWellModel], why=None
    ) -> Dict:
        """
        Caller provides the crystal well record with the fields to be updated.
        """

        # We're being given models, so serialize them into dicts to give to the sql.
        records = [model.dict() for model in models]

        count = 0
        for record in records:
            result = await self.update(
                "crystal_wells",
                record,
                f"({CommonFieldnames.UUID} = ?)",
                subs=[record[CommonFieldnames.UUID]],
                why=why,
            )
            count += result.get("count", 0)

        return {"count": count}

    # ----------------------------------------------------------------------------------------
    async def fetch_crystal_wells_filenames_serialized(
        self, limit: int = 1, why=None
    ) -> List[Dict]:
        """ """

        # Get the models from the direct call.
        models = await self.fetch_crystal_wells_filenames(limit=limit, why=why)

        # Serialize models into dicts to give to the response.
        records = [model.dict() for model in models]

        return records

    # ----------------------------------------------------------------------------------------
    async def fetch_crystal_wells_filenames(
        self, limit: int = 1, why=None
    ) -> List[CrystalWellModel]:
        """
        Filenams for ALL wells ever.
        """

        if why is None:
            why = "API fetch_crystal_wells_filenames"
        records = await self.query(
            "SELECT crystal_wells.filename"
            f" FROM crystal_wells"
            f" ORDER BY {CommonFieldnames.CREATED_ON}",
            why=why,
        )

        # Parse the records returned by sql into models.
        models = [CrystalWellModel(**record) for record in records]

        return models

    # ----------------------------------------------------------------------------------------
    async def fetch_crystal_wells_needing_autolocation_serialized(
        self, limit: int = 1, why=None
    ) -> List[Dict]:
        """ """

        # Get the models from the direct call.
        models = await self.fetch_crystal_wells_needing_autolocation(
            limit=limit, why=why
        )

        # Serialize models into dicts to give to the response.
        records = [model.dict() for model in models]

        return records

    # ----------------------------------------------------------------------------------------
    async def fetch_crystal_wells_needing_autolocation(
        self, limit: int = 1, why=None
    ) -> List[CrystalWellModel]:
        """
        Wells need an autolocation if they don't have one yet.
        """

        if why is None:
            why = "API fetch_crystal_wells_needing_autolocation"
        records = await self.query(
            "SELECT crystal_wells.*"
            f"\n  FROM crystal_wells"
            f"\n  LEFT JOIN crystal_well_autolocations"
            " ON crystal_wells.uuid = crystal_well_autolocations.crystal_well_uuid"
            "\n  WHERE crystal_well_autolocations.uuid IS NULL"
            f"\n  ORDER BY {CommonFieldnames.CREATED_ON}"
            f"\n  LIMIT {limit}",
            why=why,
        )

        # Parse the records returned by sql into models.
        models = [CrystalWellModel(**record) for record in records]

        return models

    # ----------------------------------------------------------------------------------------
    async def fetch_crystal_wells_needing_droplocation_serialized(
        self, filter: Dict, why=None
    ) -> List[Dict]:
        """
        Caller provides the filters for selecting which crystal wells.
        Returns records from the database.
        """

        # Get the models from the direct call.
        models = await self.fetch_crystal_wells_needing_droplocation(
            CrystalWellFilterModel(**filter), why=why
        )

        # Serialize models into dicts to give to the response.
        records = [model.dict() for model in models]

        return records

    # ----------------------------------------------------------------------------------------
    async def fetch_crystal_wells_needing_droplocation(
        self, filter: CrystalWellFilterModel, why=None
    ) -> List[CrystalWellNeedingDroplocationModel]:
        """
        Wells need a droplocation if they have an autolocation but no droplocation.
        """

        subs = []

        created_on = CommonFieldnames.CREATED_ON

        where = "WHERE"

        if why is None:
            why = "API fetch_crystal_wells_needing_droplocation"

        query = (
            "\nSELECT crystal_wells.*,"
            "\n  crystal_well_autolocations.auto_target_position_x,"
            "\n  crystal_well_autolocations.auto_target_position_y,"
            "\n  crystal_well_droplocations.confirmed_target_position_x,"
            "\n  crystal_well_droplocations.confirmed_target_position_y"
            "\nFROM crystal_wells"
            "\nJOIN crystal_well_autolocations ON crystal_well_autolocations.crystal_well_uuid = crystal_wells.uuid"
            "\nLEFT JOIN crystal_well_droplocations ON crystal_well_droplocations.crystal_well_uuid = crystal_wells.uuid"
        )

        # Caller wants a glob of file?
        if filter.filename_pattern is not None:
            query += (
                "\n/* Just certain filenames. */"
                f"\n{where} crystal_wells.filename GLOB ?"
            )
            subs.append(filter.filename_pattern)
            where = "AND"

        # Caller wants only those not yet confirmed?
        if filter.is_confirmed is False:
            query += (
                "\n/* Exclude crystal wells which already have confirmed drop locations. */"
                f"\n{where} crystal_wells.uuid NOT IN (SELECT crystal_well_uuid FROM crystal_well_droplocations)"
            )
            where = "AND"

        # Caller wants only those which are confirmed?
        # Confirmed means a droplocation record has been created at all (though might not have usable coordinates).
        if filter.is_confirmed is True:
            query += (
                "\n/* Include only crystal wells which already have confirmed drop locations. */"
                f"\n{where} crystal_wells.uuid IN (SELECT crystal_well_uuid FROM crystal_well_droplocations)"
            )
            where = "AND"

        # Caller wants only those which are confirmed but do not have usable coordinates?
        usable_sql = "SELECT crystal_well_uuid FROM crystal_well_droplocations WHERE confirmed_target_position_x IS NOT NULL AND confirmed_target_position_y IS NOT NULL"
        if filter.is_usable is False:
            query += (
                "\n/* Include only crystal wells which DO NOT have drop locations with usable coordinates. */"
                f"\n{where} crystal_wells.uuid NOT IN ({usable_sql})"
            )
            where = "AND"

        # Caller wants only those which are confirmed to have usable coordinates?
        if filter.is_usable is True:
            query += (
                "\n/* Include only crystal wells which have drop locations with usable coordinates. */"
                f"\n{where} crystal_wells.uuid IN ({usable_sql})"
            )
            where = "AND"

        # Caller wants results relative to anchor?
        if filter.anchor is not None:
            # Caller wants the anchor itself?
            if filter.direction is None:
                query += (
                    "\n/* Get the crystal well at the anchor. */"
                    f"\n{where} crystal_wells.uuid = ?"
                )
            # Not the anchor itself, but either side of the anchor?
            else:
                op = ">"
                if filter.direction == -1:
                    op = "<"
                query += (
                    "\n/* Get the crystal well(s) starting from the anchor. */"
                    f"\n{where} crystal_wells.created_on {op} (SELECT {created_on} FROM crystal_wells WHERE uuid = ?)"
                )
            subs.append(filter.anchor)

        sql_direction = "ASC"
        if filter.direction == -1:
            sql_direction = "DESC"

        query += f"\nORDER BY crystal_wells.{created_on} {sql_direction}"

        if filter.limit is not None:
            query += f"\nLIMIT {filter.limit}"

        records = await self.query(query, subs=subs, why=why)

        logger.debug(describe("records", records))

        # Parse the records returned by sql into models.
        models = [CrystalWellNeedingDroplocationModel(**record) for record in records]

        return models

    # ----------------------------------------------------------------------------------------
    async def originate_crystal_well_autolocations_serialized(
        self, records: List[Dict]
    ) -> None:
        # We are being given json, so parse it into models.
        models = [CrystalWellAutolocationModel(**record) for record in records]
        # Return the method doing the work.
        return await self.originate_crystal_well_autolocations(models)

    # ----------------------------------------------------------------------------------------
    async def originate_crystal_well_autolocations(
        self, models: List[CrystalWellAutolocationModel]
    ) -> None:
        """
        Caller provides the records containing fields to be created.
        """

        # We're being given models, serialize them into dicts for the sql.
        records = [model.dict() for model in models]

        return await self.insert(
            "crystal_well_autolocations",
            records,
            why="originate_crystal_well_autolocations",
        )

    # ----------------------------------------------------------------------------------------
    async def originate_crystal_well_droplocations_serialized(
        self, records: List[Dict]
    ) -> None:
        # We are being given json, so parse it into models.
        models = [CrystalWellDroplocationModel(**record) for record in records]

        # Return the method doing the work.
        return await self.originate_crystal_well_droplocations(models)

    # ----------------------------------------------------------------------------------------
    async def originate_crystal_well_droplocations(
        self, models: List[CrystalWellDroplocationModel]
    ) -> None:
        """
        Caller provides the records containing fields to be created.
        """

        # We're being given models, serialize them into dicts for the sql.
        records = [model.dict() for model in models]

        return await self.insert(
            "crystal_well_droplocations",
            records,
            why="originate_crystal_well_droplocations",
        )

    # ----------------------------------------------------------------------------------------
    async def upsert_crystal_well_droplocations_serialized(
        self, records: List[Dict], why=None
    ) -> Dict:
        # We are being given json, so parse it into models.
        models = [CrystalWellDroplocationModel(**record) for record in records]
        # Return the method doing the work.
        return await self.upsert_crystal_well_droplocations(models, why=why)

    # ----------------------------------------------------------------------------------------
    async def upsert_crystal_well_droplocations(
        self,
        models: List[CrystalWellDroplocationModel],
        why=None,
    ) -> Dict:
        """
        Caller provides the crystal well droplocation record with the fields to be updated.
        """

        if why is None:
            why = "upsert_crystal_well_droplocations"

        # We're being given models, so serialize them into dicts to give to the sql.
        records = [model.dict() for model in models]

        count = 0
        new_records = []
        for record in records:
            result = await self.update(
                "crystal_well_droplocations",
                record,
                # We upsert the droplocation record keyed on the crystal well uuid.
                "(crystal_well_uuid = ?)",
                subs=[record["crystal_well_uuid"]],
                why=why,
            )
            if result.get("count", 0) == 0:
                new_records.append(record)

            count += result.get("count", 0)

        await self.insert(
            "crystal_well_droplocations",
            new_records,
            why=why,
        )

        count += len(new_records)

        return {"count": count}

    # ----------------------------------------------------------------------------------------
    async def report_health(self):
        """"""

        report = {}

        report["alive"] = True

        return report

    # ----------------------------------------------------------------------------------------
    async def open_client_session(self):
        """"""
        # Connect to the database to create the schemas if they don't exist already.
        await self.establish_database_connection()

    # ----------------------------------------------------------------------------------------
    async def close_client_session(self):
        """"""
        logger.debug(f"[ECHDON] {callsign(self)} in aexit, calling disconnect")

        await self.disconnect()

        logger.debug(f"[ECHDON] {callsign(self)} in aexit, disconnected")
