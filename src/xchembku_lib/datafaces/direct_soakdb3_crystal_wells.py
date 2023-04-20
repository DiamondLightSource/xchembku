import logging
from typing import Dict, List, Optional

from dls_utilpack.callsign import callsign
from dls_utilpack.require import require

# Soakdb3 dataface/database.
from soakdb3_api.databases.constants import Tablenames
from soakdb3_api.datafaces.datafaces import Datafaces as Soakdb3ApiDatafaces
from soakdb3_api.models.crystal_well_model import (
    CrystalWellModel as Soakdb3CrystalWellModel,
)

from xchembku_lib.datafaces.direct_base import DirectBase

logger = logging.getLogger(__name__)


class DirectSoakdb3CrystalWells(DirectBase):
    """ """

    # ----------------------------------------------------------------------------------------
    async def append_soakdb3_crystal_wells_serialized(
        self,
        visitid: str,
        records: List[Dict],
        why: Optional[str] = None,
    ) -> Dict:
        # We are being given json, so parse it into models.
        models = [Soakdb3CrystalWellModel(**record) for record in records]
        # Return the method doing the work.
        return await self.append_soakdb3_crystal_wells(visitid, models, why=why)

    # ----------------------------------------------------------------------------------------
    async def disconnect_soakdb3_crystal_wells_mixin(self):
        """
        Called from base class disconnect.
        """

        if (
            hasattr(self, "soakdb3_dataface_client")
            and self.soakdb3_dataface_client is not None
        ):
            await self.soakdb3_dataface_client.close_client_session()

    # ----------------------------------------------------------------------------------------
    async def append_soakdb3_crystal_wells(
        self,
        visitid,
        models: List[Soakdb3CrystalWellModel],
        why="append_soakdb3_crystal_wells",
    ) -> Dict:
        """
        Append the crystal wells described by the models
        into the soakdb3 database for the given visit.

        We don't insert the same CrystalPlate/CrystalWell twice.
        """

        self.__establish_soakdb3_dataface_client()

        # Get rows of all existing plate/well pairs in the soakdb3 database.
        plate_well_rows = await self.soakdb3_dataface_client.query(  # type: ignore
            visitid,
            f"SELECT CrystalPlate, CrystalWell FROM {Tablenames.BODY}",
        )

        # Flatten the plate_well values into a list of combine plate/well records.
        plate_wells = []
        for plate_well_row in plate_well_rows:
            plate_wells.append(
                self.__plate_well(plate_well_row[0], plate_well_row[1]),
            )

        inserted_count = 0
        skipped_count = 0

        # Loop over all the models to be appended.
        id = 0
        fields = []
        for model in models:
            # Make combined plate/well name for this model.
            plate_well = self.__plate_well(
                model.CrystalPlate,
                model.CrystalWell,
            )
            # Already have this plate/well?
            if plate_well in plate_wells:
                skipped_count += 1
                continue
            inserted_count += 1
            plate_wells.append(plate_well)

            # ID for this row is next negative number, causing insert.
            id = id - 1
            # Make a row for each field in the model.
            record = model.dict()
            for field in list(record.keys()):
                # Ignore the ID field since an insert will generate a new one.
                if field == "ID":
                    continue
                fields.append(
                    {
                        "id": str(id),
                        "field": field,
                        "value": record[field],
                    }
                )

        await self.soakdb3_dataface_client.update_body_fields(  # type: ignore
            visitid,
            fields,
        )

        return {
            "skipped_count": skipped_count,
            "inserted_count": inserted_count,
        }

    # ----------------------------------------------------------------------------------------
    async def fetch_soakdb3_crystal_wells_serialized(
        self,
        visitid: str,
        why=None,
    ) -> List[Dict]:
        """
        Caller provides the filters for selecting which crystal plates.
        Returns records from the database.

        TODO: Add a query filter to fetch_crystal_wells_serialized.
        """

        # Get the models from the direct call.
        models = await self.fetch_soakdb3_crystal_wells(visitid, why=why)

        # Serialize models into dicts to give to the response.
        records = [model.dict() for model in models]

        return records

    # ----------------------------------------------------------------------------------------
    async def fetch_soakdb3_crystal_wells(
        self,
        visitid: str,
        why: Optional[str] = None,
    ) -> List[Soakdb3CrystalWellModel]:
        """"""

        self.__establish_soakdb3_dataface_client()

        # Get rows of all existing plate/well pairs in the soakdb3 database.
        records = await self.soakdb3_dataface_client.query_for_dictionary(  # type: ignore
            visitid,
            f"SELECT * FROM {Tablenames.BODY} ORDER BY ID ASC",
        )

        # Dicts are returned, so parse them into models.
        # Fields which came from the query which are not defined in the model are ignored.
        # TODO: Fetch only desired fields when querying in fetch_soakdb3_crystal_wells.
        models = [Soakdb3CrystalWellModel(**record) for record in records]

        return models

    # ----------------------------------------------------------------------------------------
    def __establish_soakdb3_dataface_client(self) -> None:
        """
        Get a soakdb3 dataface client client.

        Once a connection is made, the object reference is kept
        and the same one used as return for subsequent calls.
        """

        # TODO: Solve problem of DirectSoakdb3CrystalWells mixin constructor not getting called, and remove several # type: ignore.
        if not hasattr(self, "soakdb3_dataface_client"):
            self.soakdb3_dataface_client = None

        if self.soakdb3_dataface_client is not None:
            return

        soakdb3_specification = require(
            f"{callsign(self)} specification",
            self.specification(),
            "soakdb3_dataface_specification",
        )

        self.soakdb3_dataface_client = Soakdb3ApiDatafaces().build_object(
            soakdb3_specification
        )

    # ----------------------------------------------------------------------------------------
    def __plate_well(self, plate: str, well: str) -> str:
        """
        Make a combined string out of the plate and well pair.

        Args:
            plate (str): plate name
            well (str): well name

        Returns:
            str: plate/well combined
        """

        return f"{plate}.{well}"
