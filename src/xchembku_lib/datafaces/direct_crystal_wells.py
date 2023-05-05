import copy
import logging
from typing import Any, Dict, List

from dls_normsql.constants import CommonFieldnames

from xchembku_api.models.crystal_well_filter_model import (
    CrystalWellFilterModel,
    CrystalWellFilterSortbyEnum,
)
from xchembku_api.models.crystal_well_model import CrystalWellModel
from xchembku_api.models.crystal_well_needing_droplocation_model import (
    CrystalWellNeedingDroplocationModel,
)
from xchembku_lib.datafaces.direct_base import DirectBase

logger = logging.getLogger(__name__)


class DirectCrystalWells(DirectBase):
    """ """

    # ----------------------------------------------------------------------------------------
    async def upsert_crystal_wells_serialized(
        self,
        records: List[Dict],
        why=None,
    ) -> Dict:
        # We are being given json, so parse it into models.
        models = [CrystalWellModel(**record) for record in records]
        # Return the method doing the work.
        return await self.upsert_crystal_wells(models, why=why)

    # ----------------------------------------------------------------------------------------
    async def upsert_crystal_wells(
        self,
        models: List[CrystalWellModel],
        why="upsert_crystal_wells",
    ) -> Dict:
        """
        Caller provides the crystal well record with the fields to be updated.

        We don't insert the same filename twice.

        TODO: Consider an alternate way besides filename to distinguish duplicate crystal wells in upsert.

        TODO: Find more efficient way to upsert_crystal_wells in batch.
        """

        inserted_count = 0
        updated_count = 0

        # Loop over all the models to be upserted.
        for model in models:
            # Find any existing record for this model object.
            records = await self.query(
                "SELECT * FROM crystal_wells WHERE filename = ?",
                subs=[model.filename],
                why=why,
            )

            if len(records) > 0:
                # Make a copy of the model record and remove some fields not to update.
                model_copy = copy.deepcopy(model.dict())
                model_copy.pop(CommonFieldnames.UUID)
                model_copy.pop(CommonFieldnames.CREATED_ON)
                model_copy.pop("filename")
                model_copy.pop("crystal_plate_uuid")
                result = await self.update(
                    "crystal_wells",
                    model_copy,
                    "(filename = ?)",
                    subs=[model.filename],
                    why=why,
                )
                updated_count += result.get("count", 0)
            else:
                await self.insert(
                    "crystal_wells",
                    [model.dict()],
                    why=why,
                )
                inserted_count += 1

        return {
            "updated_count": updated_count,
            "inserted_count": inserted_count,
        }

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
            "SELECT"
            " crystal_wells.uuid,"
            " crystal_wells.position,"
            " crystal_wells.filename,"
            " crystal_wells.crystal_plate_uuid,"
            f" crystal_wells.{CommonFieldnames.CREATED_ON}"
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
        Wells need a droplocation if they have an autolocation.
        """

        # Caller wants results relative to anchor?
        if filter.anchor is not None and filter.direction is not None:
            return await self.__fetch_crystal_wells_needing_droplocation_hard(
                filter, why=why
            )
        # Query can be made easier if there is no anchor with direction involved.
        else:
            return await self.__fetch_crystal_wells_needing_droplocation_easy(
                filter, why=why
            )

    # ----------------------------------------------------------------------------------------
    async def __fetch_crystal_wells_needing_droplocation_easy(
        self, filter: CrystalWellFilterModel, why=None
    ) -> List[CrystalWellNeedingDroplocationModel]:
        """
        Wells need a droplocation if they have an autolocation.
        """

        if why is None:
            why = "API fetch_crystal_wells_needing_droplocation"

        # Build the individual pieces of the SQL query.
        subs: List[Any] = []
        orderby = self.__build_orderby(filter)
        where = self.__build_where(filter, subs)
        fields = self.__build_fields(filter)
        joins = self.__build_joins(filter)

        # Glue them together.
        main_query = "\nSELECT" + fields + joins + where + "\n" + orderby

        if filter.limit is not None:
            main_query += f"\nLIMIT {filter.limit}"

        # Query the database.
        records = await self.query(main_query, subs=subs, why=why)

        # Parse the records returned by sql into models.
        models = [CrystalWellNeedingDroplocationModel(**record) for record in records]

        return models

    # ----------------------------------------------------------------------------------------
    async def __fetch_crystal_wells_needing_droplocation_hard(
        self, filter: CrystalWellFilterModel, why=None
    ) -> List[CrystalWellNeedingDroplocationModel]:
        """
        This is the query when we want records relative from an anchor record.

        Since this involves complex subqueries, we limit use of this
        to when we're looking only at records in a specific visit or plate.
        """

        if filter.visit is None:
            raise RuntimeError(
                "programming error: no visit supplied with relative crystal well filter"
            )

        if why is None:
            why = "API fetch_crystal_wells_needing_droplocation"

        # Build the individual pieces of the SQL query.
        subs: List[Any] = []
        orderby = self.__build_orderby(filter)
        where = self.__build_where(filter, subs)
        fields = self.__build_fields(filter)
        joins = self.__build_joins(filter)

        # We need the row number to be in both the main and sub query.
        row_number = f"\n  ROW_NUMBER() OVER ({orderby}) AS ordered_row_number"
        fields = row_number + "," + fields

        # Main query gets the actual results.
        main_query = "SELECT" + fields + joins + where

        # Build another "where" since it may add subs.
        where = self.__build_where(filter, subs)

        # Sub query computes row_numbers under the same filter in the same order as the main query.
        sub_query = "\nSELECT\n  crystal_wells.uuid," + row_number + joins + where

        # Do the main query, but filter the results by the subquery based on matching row numbers.
        full_query = (
            f"\nSELECT * FROM (\n{main_query}\n) AS main_query"
            f"\n/* Match row_numbers starting from the anchor {filter.anchor}. */"
            "\nWHERE ordered_row_number >"
            f"\n  (SELECT ordered_row_number FROM ({sub_query}\n) AS sub_query"
            f"\n    WHERE sub_query.uuid = ?)"
            f"\n    ORDER BY ordered_row_number"
        )
        subs.append(filter.anchor)

        if filter.limit is not None:
            full_query += f"\nLIMIT {filter.limit}"

        # Do the actual query.
        records = await self.query(full_query, subs=subs, why=why)

        # Parse the records returned by sql into models.
        models = [CrystalWellNeedingDroplocationModel(**record) for record in records]

        return models

    # ----------------------------------------------------------------------------------------
    def __build_fields(
        self,
        filter: CrystalWellFilterModel,
    ) -> str:
        """
        Wells need a droplocation if they have an autolocation.
        """

        fields = (
            "\n  crystal_wells.*,"
            "\n  crystal_well_autolocations.auto_target_x,"
            "\n  crystal_well_autolocations.auto_target_y,"
            "\n  crystal_well_autolocations.well_centroid_x,"
            "\n  crystal_well_autolocations.well_centroid_y,"
            "\n  crystal_well_autolocations.drop_detected,"
            "\n  crystal_well_autolocations.number_of_crystals,"
            "\n  crystal_well_droplocations.confirmed_target_x,"
            "\n  crystal_well_droplocations.confirmed_target_y,"
            "\n  crystal_well_droplocations.confirmed_microns_x,"
            "\n  crystal_well_droplocations.confirmed_microns_y,"
            "\n  crystal_well_droplocations.is_usable,"
            "\n  crystal_plates.visit,"
            "\n  crystal_plates.thing_type AS crystal_plate_thing_type"
        )

        return fields

    # ----------------------------------------------------------------------------------------
    def __build_joins(
        self,
        filter: CrystalWellFilterModel,
    ) -> str:
        """
        Wells need a droplocation if they have an autolocation.
        """

        joins = (
            "\nFROM crystal_wells"
            "\nJOIN crystal_well_autolocations ON crystal_well_autolocations.crystal_well_uuid = crystal_wells.uuid"
            "\nLEFT JOIN crystal_well_droplocations ON crystal_well_droplocations.crystal_well_uuid = crystal_wells.uuid"
            "\nLEFT JOIN crystal_plates ON crystal_plates.uuid = crystal_wells.crystal_plate_uuid"
        )

        return joins

    # ----------------------------------------------------------------------------------------
    def __build_where(
        self,
        filter: CrystalWellFilterModel,
        subs: List[Any],
    ) -> str:
        """
        Wells need a droplocation if they have an autolocation.
        """

        where = "WHERE"
        sql = ""

        # Caller wants a glob of file?
        if filter.filename_pattern is not None:
            sql += (
                "\n/* Just certain filenames. */"
                f"\n{where} crystal_wells.filename GLOB ?"
            )
            subs.append(filter.filename_pattern)
            where = "AND"

        # Caller wants specific barcode?
        if filter.barcode is not None:
            sql += (
                f"\n/* Just wells on plate with barcode '{filter.barcode}'. */"
                f"\n{where} crystal_plates.barcode = ?"
            )
            subs.append(filter.barcode)
            where = "AND"

        # Caller wants specific visit?
        if filter.visit is not None:
            sql += (
                f"\n/* Just wells on plates with visit '{filter.visit}'. */"
                f"\n{where} crystal_plates.visit = ?"
            )
            subs.append(filter.visit)
            where = "AND"

        # Caller wants only those not yet decided?
        if filter.is_decided is False:
            sql += (
                "\n/* Include only crystal wells which have not had a decision made. */"
                f"\n{where} crystal_well_droplocations.is_usable IS NULL"
            )
            where = "AND"

        # Caller wants only those which are decided?
        # Confirmed means a droplocation record has been created at all (though might not have usable coordinates).
        if filter.is_decided is True:
            sql += (
                "\n/* Include only crystal wells which have a decision made. */"
                f"\n{where} crystal_well_droplocations.is_usable IS NOT NULL"
            )
            where = "AND"

        # Caller wants only those which are decided but do or don't have usable coordinates?
        if filter.is_usable is not None:
            sql += (
                f"\n/* Include only crystal wells which have filter.is_usable = {filter.is_usable}. */"
                f"\n{where} crystal_well_droplocations.is_usable = ?"
            )
            subs.append(filter.is_usable)
            where = "AND"

        # Caller wants just the anchor record?
        if filter.anchor is not None and filter.direction is None:
            sql += (
                "\n/* Get the crystal well at the anchor. */"
                f"\n{where} crystal_wells.uuid = ?"
            )
            subs.append(filter.anchor)

        return sql

    # ----------------------------------------------------------------------------------------
    def __build_orderby(
        self,
        filter: CrystalWellFilterModel,
    ) -> str:

        sql = ""

        position_direction = "ASC"
        if filter.direction == -1:
            position_direction = "DESC"

        # Filter says order by number of crystals?
        if filter.sortby == CrystalWellFilterSortbyEnum.NUMBER_OF_CRYSTALS:
            crystals_direction = "DESC"
            if filter.direction == -1:
                crystals_direction = "ASC"

            # If duplicate crystals, use position as tie breaker.
            order_by = f"crystal_well_autolocations.number_of_crystals {crystals_direction}, crystal_wells.position {position_direction}"
        else:
            order_by = f"crystal_wells.position {position_direction}"

        sql += f"ORDER BY {order_by}"

        return sql
