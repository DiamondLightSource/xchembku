import logging
from typing import Dict, List

from dls_normsql.constants import CommonFieldnames
from dls_utilpack.describe import describe

from xchembku_api.models.crystal_plate_model import CrystalPlateModel
from xchembku_lib.datafaces.direct_base import DirectBase

logger = logging.getLogger(__name__)


class DirectCrystalPlates(DirectBase):
    """ """

    # ----------------------------------------------------------------------------------------
    async def originate_crystal_plates_serialized(self, records: List[Dict]) -> None:
        # We are being given json, so parse it into models.
        models = [CrystalPlateModel(**record) for record in records]
        # Return the method doing the work.
        return await self.originate_crystal_plates(models)

    # ----------------------------------------------------------------------------------------
    async def originate_crystal_plates(self, models: List[CrystalPlateModel]) -> None:
        """
        Caller provides the records containing fields to be created.
        The filename field should be unique in all records.
        """

        # We're being given models, so serialize them into dicts to give to the sql.
        records = [model.dict() for model in models]

        return await self.insert(
            "crystal_plates",
            records,
            why="originate_crystal_plates",
        )

    # ----------------------------------------------------------------------------------------
    async def update_crystal_plates_serialized(self, records: List[Dict]) -> Dict:
        # We are being given json, so parse it into models.
        models = [CrystalPlateModel(**record) for record in records]
        # Return the method doing the work.
        return await self.update_crystal_plates(models)

    # ----------------------------------------------------------------------------------------
    async def update_crystal_plates(
        self, models: List[CrystalPlateModel], why=None
    ) -> Dict:
        """
        Caller provides the crystal plate record with the fields to be updated.
        """

        # We're being given models, so serialize them into dicts to give to the sql.
        records = [model.dict() for model in models]

        count = 0
        for record in records:
            result = await self.update(
                "crystal_plates",
                record,
                f"({CommonFieldnames.UUID} = ?)",
                subs=[record[CommonFieldnames.UUID]],
                why=why,
            )
            count += result.get("count", 0)

        return {"count": count}
