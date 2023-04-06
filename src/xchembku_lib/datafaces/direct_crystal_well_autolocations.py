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
from xchembku_lib.datafaces.direct_crystal_well_droplocations import (
    DirectCrystalWellDroplocations,
)

logger = logging.getLogger(__name__)


class DirectCrystalWellAutolocations:
    """ """

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
