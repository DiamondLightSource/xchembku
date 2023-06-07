import logging
from typing import Dict, List, Optional

from soakdb3_api.models.crystal_well_model import (
    CrystalWellModel as Soakdb3CrystalWellModel,
)

# Class for an aiohttp client.
from xchembku_api.aiohttp_client import AiohttpClient

# Dataface protocolj things.
from xchembku_api.datafaces.constants import Commands, Keywords
from xchembku_api.models.crystal_plate_filter_model import CrystalPlateFilterModel
from xchembku_api.models.crystal_plate_model import CrystalPlateModel
from xchembku_api.models.crystal_plate_report_model import CrystalPlateReportModel
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

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------
class Aiohttp(AiohttpClient):
    """
    Object implementing client side API for talking to the xchembku_dataface server.
    Please see doctopic [A01].
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification):

        # We will get an umbrella specification which must contain an aiohttp_specification within it.
        AiohttpClient.__init__(
            self,
            specification["type_specific_tbd"]["aiohttp_specification"],
        )

    # ----------------------------------------------------------------------------------------
    async def query(self, sql, subs=None, why: Optional[str] = None):
        """"""
        return await self.__send_protocolj(
            "query",
            sql,
            subs=subs,
            why=why,
        )

    # ----------------------------------------------------------------------------------------
    async def execute(self, sql, subs=None, why: Optional[str] = None):
        """"""
        return await self.__send_protocolj(
            "execute",
            sql,
            subs=subs,
            why=why,
            as_transaction=True,
        )

    # ----------------------------------------------------------------------------------------
    async def insert(self, table_name, records, why: Optional[str] = None):
        """"""
        return await self.__send_protocolj(
            "insert",
            table_name,
            records,
            why=why,
            as_transaction=True,
        )

    # ----------------------------------------------------------------------------------------
    async def update(
        self, table_name, record, where, subs=None, why: Optional[str] = None
    ):
        """"""
        return await self.__send_protocolj(
            "update",
            table_name,
            record,
            where,
            subs=subs,
            why=why,
            as_transaction=True,
        )

    # ----------------------------------------------------------------------------------------
    async def upsert_crystal_plates(
        self,
        models: List[CrystalPlateModel],
        why: Optional[str] = None,
    ) -> None:
        """"""

        records: List[Dict] = [model.dict() for model in models]
        await self.__send_protocolj(
            "upsert_crystal_plates_serialized",
            records,
            why=why,
            as_transaction=True,
        )

        return None

    # ----------------------------------------------------------------------------------------
    async def fetch_crystal_plates(
        self,
        filter: CrystalPlateFilterModel,
        why: Optional[str] = None,
    ) -> List[CrystalPlateModel]:
        """"""

        records = await self.__send_protocolj(
            "fetch_crystal_plates_serialized",
            filter=filter.dict(),
            why=why,
        )

        # Dicts are returned, so parse them into models.
        models = [CrystalPlateModel(**record) for record in records]

        return models

    # ----------------------------------------------------------------------------------------
    async def report_crystal_plates(
        self,
        filter: CrystalPlateFilterModel,
        why: Optional[str] = None,
    ) -> List[CrystalPlateReportModel]:
        """"""

        records = await self.__send_protocolj(
            "report_crystal_plates_serialized",
            filter=filter.dict(),
            why=why,
        )

        # Dicts are returned, so parse them into models.
        models = [CrystalPlateReportModel(**record) for record in records]

        return models

    # ----------------------------------------------------------------------------------------
    async def fetch_crystal_wells_filenames(
        self,
        limit: int = 1,
        why: Optional[str] = None,
    ) -> List[CrystalWellModel]:
        """"""

        records = await self.__send_protocolj(
            "fetch_crystal_wells_filenames_serialized",
            limit=limit,
            why=why,
        )

        # Dicts are returned, so parse them into models.
        models = [CrystalWellModel(**record) for record in records]

        return models

    # ----------------------------------------------------------------------------------------
    async def upsert_crystal_wells(
        self,
        models: List[CrystalWellModel],
    ) -> None:
        """"""

        records: List[Dict] = [model.dict() for model in models]
        await self.__send_protocolj(
            "upsert_crystal_wells_serialized",
            records,
            as_transaction=True,
        )

        return None

    # ----------------------------------------------------------------------------------------
    async def update_crystal_wells(
        self,
        records,
        why: Optional[str] = None,
        as_transaction=True,
    ) -> Dict:
        """"""

        return await self.__send_protocolj(
            "update_crystal_wells_serialized",
            records,
            why=why,
        )

    # ----------------------------------------------------------------------------------------
    async def fetch_crystal_wells_needing_autolocation(
        self,
        limit: int = 1,
        why: Optional[str] = None,
    ) -> List[CrystalWellModel]:
        """"""

        records = await self.__send_protocolj(
            "fetch_crystal_wells_needing_autolocation_serialized",
            limit=limit,
            why=why,
        )

        # Dicts are returned, so parse them into models.
        models = [CrystalWellModel(**record) for record in records]

        return models

    # ----------------------------------------------------------------------------------------
    async def fetch_crystal_wells_needing_droplocation(
        self,
        filter: CrystalWellFilterModel,
        why: Optional[str] = None,
    ) -> List[CrystalWellNeedingDroplocationModel]:
        """"""

        records = await self.__send_protocolj(
            "fetch_crystal_wells_needing_droplocation_serialized",
            filter.dict(),
            why=why,
        )

        # Dicts are returned, so parse them into models.
        models = [CrystalWellNeedingDroplocationModel(**record) for record in records]

        return models

    # ----------------------------------------------------------------------------------------
    async def originate_crystal_well_autolocations(
        self, models: List[CrystalWellAutolocationModel]
    ) -> None:
        """"""

        records: List[Dict] = [model.dict() for model in models]
        await self.__send_protocolj(
            "originate_crystal_well_autolocations_serialized",
            records,
            as_transaction=True,
        )

        return None

    # ----------------------------------------------------------------------------------------
    async def upsert_crystal_well_droplocations(
        self,
        models: List[CrystalWellDroplocationModel],
        only_fields: Optional[List[str]] = None,
        why: Optional[str] = None,
    ) -> None:
        """"""

        records: List[Dict] = [model.dict() for model in models]
        await self.__send_protocolj(
            "upsert_crystal_well_droplocations_serialized",
            records,
            only_fields=only_fields,
            why=why,
            as_transaction=True,
        )

        return None

    # ----------------------------------------------------------------------------------------
    async def inject_soakdb3_crystal_wells(
        self,
        visitid: str,
        models: List[Soakdb3CrystalWellModel],
        why: Optional[str] = None,
    ) -> Dict:
        """"""

        records: List[Dict] = [model.dict() for model in models]
        result = await self.__send_protocolj(
            "inject_soakdb3_crystal_wells_serialized",
            visitid,
            records,
            why=why,
            as_transaction=True,
        )
        return result

    # ----------------------------------------------------------------------------------------
    async def fetch_soakdb3_crystal_wells(
        self,
        visitid: str,
        why: Optional[str] = None,
    ) -> List[Soakdb3CrystalWellModel]:
        """"""

        records = await self.__send_protocolj(
            "fetch_soakdb3_crystal_wells_serialized",
            visitid,
            why=why,
        )

        # Dicts are returned, so parse them into models.
        models = [Soakdb3CrystalWellModel(**record) for record in records]

        return models

    # ----------------------------------------------------------------------------------------
    async def __send_protocolj(self, function, *args, **kwargs):
        """"""

        return await self.client_protocolj(
            {
                Keywords.COMMAND: Commands.EXECUTE,
                Keywords.PAYLOAD: {
                    "function": function,
                    "args": args,
                    "kwargs": kwargs,
                },
            },
        )
