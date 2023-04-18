import copy
import logging
from threading import RLock
from typing import Dict, List, Optional

from dls_normsql.constants import CommonFieldnames
from dls_utilpack.describe import describe

from xchembku_api.models.crystal_well_droplocation_model import (
    CrystalWellDroplocationModel,
)
from xchembku_lib.datafaces.direct_base import DirectBase

logger = logging.getLogger(__name__)

# Module-level lock to keep upsert atomic.
upsert_lock = RLock()


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
        self,
        records: List[Dict],
        only_fields: Optional[List[str]] = None,
        why=None,
    ) -> Dict:
        # We are being given json, so parse it into models.
        models = [CrystalWellDroplocationModel(**record) for record in records]
        # Return the method doing the work.
        return await self.upsert_crystal_well_droplocations(
            models,
            only_fields=only_fields,
            why=why,
        )

    # ----------------------------------------------------------------------------------------
    async def upsert_crystal_well_droplocations(
        self,
        models: List[CrystalWellDroplocationModel],
        only_fields: Optional[List[str]] = None,
        why=None,
    ) -> Dict:
        """
        Caller provides the crystal well droplocation record with the fields to be updated.

        We don't insert for the same crystal_well_uuid twice.

        TODO: Find more efficient way to upsert_crystal_well_droplocations in batch.
        """

        if why is None:
            why = "upsert_crystal_well_droplocations"

        inserted_count = 0
        updated_count = 0

        # Loop over all the models to be upserted.
        for model in models:
            with upsert_lock:
                # Find any existing record for this model object.
                records = await self.query(
                    "SELECT * FROM crystal_well_droplocations WHERE crystal_well_uuid = ?",
                    subs=[model.crystal_well_uuid],
                    why=why,
                )

                if len(records) > 0:
                    logger.debug(
                        describe(
                            "crystal_well_droplocation record before update", records[0]
                        )
                    )
                    # Make a copy of the model record and remove some fields not to update.
                    model_dict = copy.deepcopy(model.dict())
                    model_dict.pop(CommonFieldnames.UUID)
                    model_dict.pop(CommonFieldnames.CREATED_ON)
                    model_dict.pop("crystal_well_uuid")
                    if only_fields is not None:
                        for field in list(model_dict.keys()):
                            if field not in only_fields:
                                model_dict.pop(field)

                    result = await self.update(
                        "crystal_well_droplocations",
                        model_dict,
                        "(crystal_well_uuid = ?)",
                        subs=[model.crystal_well_uuid],
                        why=why,
                    )
                    updated_count += result.get("count", 0)

                    # Find any existing record for this model object.
                    records = await self.query(
                        "SELECT * FROM crystal_well_droplocations WHERE crystal_well_uuid = ?",
                        subs=[model.crystal_well_uuid],
                        why=why,
                    )
                    logger.debug(
                        describe(
                            "crystal_well_droplocation record after update", records[0]
                        )
                    )

                else:
                    await self.insert(
                        "crystal_well_droplocations",
                        [model.dict()],
                        why=why,
                    )
                    inserted_count += 1

        return {
            "updated_count": updated_count,
            "inserted_count": inserted_count,
        }
