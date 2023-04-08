import copy
import logging
from typing import Dict, List, Union

from dls_normsql.constants import CommonFieldnames
from dls_utilpack.describe import describe

from xchembku_api.models.crystal_plate_filter_model import CrystalPlateFilterModel
from xchembku_api.models.crystal_plate_model import CrystalPlateModel
from xchembku_lib.datafaces.direct_base import DirectBase

logger = logging.getLogger(__name__)


class DirectCrystalPlates(DirectBase):
    """ """

    # ----------------------------------------------------------------------------------------
    async def upsert_crystal_plates_serialized(
        self,
        records: List[Dict],
        why=None,
    ) -> Dict:
        # We are being given json, so parse it into models.
        models = [CrystalPlateModel(**record) for record in records]
        # Return the method doing the work.
        return await self.upsert_crystal_plates(models, why=why)

    # ----------------------------------------------------------------------------------------
    async def upsert_crystal_plates(
        self,
        models: List[CrystalPlateModel],
        why="upsert_crystal_plates",
    ) -> Dict:
        """
        Caller provides the crystal plate record with the fields to be updated.
        """

        inserted_count = 0
        updated_count = 0

        # Loop over all the models to be upserted.
        for model in models:
            # Find any existing record for this model object.
            records = await self.query(
                "SELECT * FROM crystal_plates WHERE formulatrix__plate__id = ?",
                subs=[model.formulatrix__plate__id],
                why=why,
            )

            if len(records) > 0:
                # Make a copy of the model record and remove some fields not to update.
                model_copy = copy.deepcopy(model.dict())
                model_copy.pop(CommonFieldnames.UUID)
                model_copy.pop(CommonFieldnames.CREATED_ON)
                model_copy.pop("formulatrix__plate__id")
                result = await self.update(
                    "crystal_plates",
                    model_copy,
                    "(formulatrix__plate__id = ?)",
                    subs=[model.formulatrix__plate__id],
                    why=why,
                )
                updated_count += result.get("count", 0)
            else:
                await self.insert(
                    "crystal_plates",
                    [model.dict()],
                    why=why,
                )
                inserted_count += 1

        return {
            "updated_count": updated_count,
            "inserted_count": inserted_count,
        }

    # ----------------------------------------------------------------------------------------
    async def fetch_crystal_plates_serialized(
        self, filter: Dict, why=None
    ) -> List[Dict]:
        """
        Caller provides the filters for selecting which crystal plates.
        Returns records from the database.
        """

        # Get the models from the direct call.
        models = await self.fetch_crystal_plates(
            CrystalPlateFilterModel(**filter), why=why
        )

        # Serialize models into dicts to give to the response.
        records = [model.dict() for model in models]

        return records

    # ----------------------------------------------------------------------------------------
    async def fetch_crystal_plates(
        self, filter: CrystalPlateFilterModel, why=None
    ) -> List[CrystalPlateModel]:
        """
        Plates need a droplocation if they have an autolocation but no droplocation.
        """

        subs: List[Union[str, int]] = []

        where = "WHERE"

        if why is None:
            why = "API fetch_crystal_plates"

        query = "\nSELECT crystal_plates.*" "\nFROM crystal_plates"

        if filter.uuid is not None:
            query += f"\n{where} uuid = ?"
            subs.append(filter.uuid)
            where = "AND"

        if filter.barcode is not None:
            query += f"\n{where} barcode = ?"
            subs.append(filter.barcode)
            where = "AND"

        if filter.from_formulatrix__plate__id is not None:
            if filter.direction == -1:
                query += f"\n{where} formulatrix__plate__id < ?"
            else:
                query += f"\n{where} formulatrix__plate__id > ?"
            subs.append(filter.from_formulatrix__plate__id)
            where = "AND"

        sql_direction = "ASC"
        if filter.direction == -1:
            sql_direction = "DESC"

        query += f"\nORDER BY crystal_plates.formulatrix__plate__id {sql_direction}"

        if filter.limit is not None:
            query += f"\nLIMIT {filter.limit}"

        records = await self.query(query, subs=subs, why=why)

        logger.debug(describe("records", records))

        # Parse the records returned by sql into models.
        models = [CrystalPlateModel(**record) for record in records]

        return models
