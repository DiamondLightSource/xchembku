import copy
import logging
from typing import Any, Dict, List

from dls_normsql.constants import CommonFieldnames

from xchembku_api.models.crystal_well_filter_model import CrystalWellFilterModel
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
        Wells need a droplocation if they have an autolocation but no droplocation.
        """

        subs: List[Any] = []

        created_on = CommonFieldnames.CREATED_ON

        where = "WHERE"

        if why is None:
            why = "API fetch_crystal_wells_needing_droplocation"

        query = (
            "\nSELECT crystal_wells.*,"
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
            "\nFROM crystal_wells"
            "\nJOIN crystal_well_autolocations ON crystal_well_autolocations.crystal_well_uuid = crystal_wells.uuid"
            "\nLEFT JOIN crystal_well_droplocations ON crystal_well_droplocations.crystal_well_uuid = crystal_wells.uuid"
            "\nLEFT JOIN crystal_plates ON crystal_plates.uuid = crystal_wells.crystal_plate_uuid"
        )

        # Caller wants a glob of file?
        if filter.filename_pattern is not None:
            query += (
                "\n/* Just certain filenames. */"
                f"\n{where} crystal_wells.filename GLOB ?"
            )
            subs.append(filter.filename_pattern)
            where = "AND"

        # Caller wants specific barcode?
        if filter.barcode is not None:
            query += (
                f"\n/* Just a wells on plates with barcode '{filter.barcode}'. */"
                f"\n{where} crystal_plates.barcode = ?"
            )
            subs.append(filter.barcode)
            where = "AND"

        # Caller wants specific visit?
        if filter.visit is not None:
            query += (
                f"\n/* Just a wells on plates with visit '{filter.visit}'. */"
                f"\n{where} crystal_plates.visit = ?"
            )
            subs.append(filter.visit)
            where = "AND"

        # Caller wants only those not yet decided?
        if filter.is_decided is False:
            query += (
                "\n/* Include only crystal wells which have not had a decision made. */"
                f"\n{where} crystal_well_droplocations.is_usable IS NULL"
            )
            where = "AND"

        # Caller wants only those which are decided?
        # Confirmed means a droplocation record has been created at all (though might not have usable coordinates).
        if filter.is_decided is True:
            query += (
                "\n/* Include only crystal wells which have a decision made. */"
                f"\n{where} crystal_well_droplocations.is_usable IS NOT NULL"
            )
            where = "AND"

        # Caller wants only those which are decided but do or don't have usable coordinates?
        if filter.is_usable is not None:
            query += (
                f"\n/* Include only crystal wells which have filter.is_usable = {filter.is_usable}. */"
                f"\n{where} crystal_well_droplocations.is_usable = ?"
            )
            subs.append(filter.is_usable)
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
                    f"\n/* Get the crystal well(s) starting from the anchor {filter.anchor}. */"
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

        # Parse the records returned by sql into models.
        models = [CrystalWellNeedingDroplocationModel(**record) for record in records]

        return models
