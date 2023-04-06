import logging
from typing import Dict, List

from xchembku_api.models.crystal_well_droplocation_model import (
    CrystalWellDroplocationModel,
)
from xchembku_lib.datafaces.direct_base import DirectBase

logger = logging.getLogger(__name__)


class DirectCrystalWellDroplocations(DirectBase):
    """ """

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
