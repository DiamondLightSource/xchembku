import logging
from typing import Dict, List, Optional

# Class for an aiohttp client.
from xchembku_api.aiohttp_client import AiohttpClient

# Dataface protocolj things.
from xchembku_api.datafaces.constants import Commands, Keywords
from xchembku_api.models.crystal_well_autolocation_model import (
    CrystalWellAutolocationModel,
)
from xchembku_api.models.crystal_well_model import CrystalWellModel

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------
class Aiohttp:
    """
    Object implementing client side API for talking to the xchembku_dataface server.
    Please see doctopic [A01].
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None):
        self.__specification = specification

        self.__aiohttp_client = AiohttpClient(
            specification["type_specific_tbd"]["aiohttp_specification"],
        )

    # ----------------------------------------------------------------------------------------
    def specification(self):
        return self.__specification

    # ----------------------------------------------------------------------------------------
    async def query(self, sql, subs=None, why: Optional[str] = None):
        """"""
        return await self.__send_protocolj("query", sql, subs=subs, why=why)

    # ----------------------------------------------------------------------------------------
    async def execute(self, sql, subs=None, why: Optional[str] = None):
        """"""
        return await self.__send_protocolj("execute", sql, subs=subs, why=why)

    # ----------------------------------------------------------------------------------------
    async def insert(self, table_name, records, why: Optional[str] = None):
        """"""
        return await self.__send_protocolj(
            "insert",
            table_name,
            records,
            why=why,
        )

    # ----------------------------------------------------------------------------------------
    async def update(
        self, table_name, record, where, subs=None, why: Optional[str] = None
    ):
        """"""
        return await self.__send_protocolj(
            "update", table_name, record, where, subs=subs, why=why
        )

    # ----------------------------------------------------------------------------------------
    async def originate_crystal_wells(
        self,
        models: List[CrystalWellModel],
    ) -> None:
        """"""

        records: List[Dict] = [model.dict() for model in models]
        await self.__send_protocolj(
            "originate_crystal_wells_serialized",
            records,
        )

        return None

    # ----------------------------------------------------------------------------------------
    async def update_crystal_wells(
        self,
        records,
        why: Optional[str] = None,
    ) -> Dict:
        """"""

        return await self.__send_protocolj(
            "update_crystal_wells_serialized",
            records,
            why=why,
        )

    # ----------------------------------------------------------------------------------------
    async def fetch_crystal_wells_filenames(
        self,
        why: Optional[str] = None,
    ) -> List[CrystalWellModel]:
        """"""

        records = await self.__send_protocolj(
            "fetch_crystal_wells_filenames_serialized",
            why=why,
        )

        # Dicts are returned, so parse them into models.
        models = [CrystalWellModel(**record) for record in records]

        return models

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
        limit: int = 1,
        why: Optional[str] = None,
    ) -> List[CrystalWellModel]:
        """"""

        records = await self.__send_protocolj(
            "fetch_crystal_wells_needing_droplocation_serialized",
            limit=limit,
            why=why,
        )

        # Dicts are returned, so parse them into models.
        models = [CrystalWellModel(**record) for record in records]

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
        )

        return None

    # ----------------------------------------------------------------------------------------
    async def originate_crystal_well_droplocations(
        self, models: List[CrystalWellAutolocationModel]
    ) -> None:
        """"""

        records: List[Dict] = [model.dict() for model in models]
        await self.__send_protocolj(
            "originate_crystal_well_droplocations_serialized",
            records,
        )

        return None

    # ----------------------------------------------------------------------------------------
    async def report_health(self):
        """"""
        return await self.__send_protocolj("report_health")

    # ----------------------------------------------------------------------------------------
    async def set_cookie(self, cookie_dict):
        """ """
        return await self.__send_protocolj("set_cookie", cookie_dict)

    # ----------------------------------------------------------------------------------------
    async def get_cookie(self, cookie_uuid):
        """
        Get single cookie from its uuid.
        Returns database record format.
        """
        return await self.__send_protocolj("get_cookie", cookie_uuid)

    # ----------------------------------------------------------------------------------------
    async def update_cookie(self, row):
        """"""
        return await self.__send_protocolj("update_cookie", row)

    # ----------------------------------------------------------------------------------------
    async def __send_protocolj(self, function, *args, **kwargs):
        """"""

        return await self.__aiohttp_client.client_protocolj(
            {
                Keywords.COMMAND: Commands.EXECUTE,
                Keywords.PAYLOAD: {
                    "function": function,
                    "args": args,
                    "kwargs": kwargs,
                },
            },
        )

    # ----------------------------------------------------------------------------------------
    async def close_client_session(self):
        """"""

        if self.__aiohttp_client is not None:
            await self.__aiohttp_client.close_client_session()

    # ----------------------------------------------------------------------------------------
    async def client_report_health(self):
        """"""

        return await self.__aiohttp_client.client_report_health()
