import logging
from typing import Dict, List, Optional

from dls_utilpack.callsign import callsign
from dls_utilpack.describe import describe
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
    async def inject_soakdb3_crystal_wells_serialized(
        self,
        visitid: str,
        records: List[Dict],
        why: Optional[str] = None,
    ) -> Dict:
        # We are being given json, so parse it into models.
        models = [Soakdb3CrystalWellModel(**record) for record in records]
        # Return the method doing the work.
        return await self.inject_soakdb3_crystal_wells(visitid, models, why=why)

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
    async def inject_soakdb3_crystal_wells(
        self,
        visitid,
        models: List[Soakdb3CrystalWellModel],
        why="inject_soakdb3_crystal_wells",
    ) -> Dict:
        """
        Append the crystal wells described by the models
        into the soakdb3 database for the given visit.

        We don't insert the same CrystalPlate/CrystalWell twice.
        """

        self.__establish_soakdb3_dataface_client()

        # Get the necessary values from the (single) head table row.
        head_rows = await self.soakdb3_dataface_client.query_for_dictionary(  # type: ignore
            visitid,
            f"SELECT Protein, DropVolume FROM {Tablenames.HEAD}",
        )
        protein = head_rows[0]["Protein"]
        drop_volume = head_rows[0]["DropVolume"]

        logger.debug(describe("head row protein", protein))
        logger.debug(describe("head row drop_volume", drop_volume))

        # Get rows of all existing plate/well pairs in the soakdb3 database.
        plate_well_rows = await self.soakdb3_dataface_client.query(  # type: ignore
            visitid,
            f"SELECT ID, CrystalPlate, CrystalWell FROM {Tablenames.BODY} ORDER BY ID ASC",
        )

        # Flatten the plate_well values into a list of combine plate/well records.
        plate_wells = []
        blank_row_ids = []
        for plate_well_row in plate_well_rows:
            # This is a row with empty or blank CrystalPlate?
            if plate_well_row[1] is None or plate_well_row[1] == "":
                # Remember the ID of this row so we can update it.
                blank_row_ids.append(plate_well_row[0])
            else:
                plate_wells.append(
                    self.__plate_well(plate_well_row[1], plate_well_row[2]),
                )

        updated_count = 0
        inserted_count = 0
        skipped_count = 0

        # Loop over all the models to be appended.
        id_to_insert = 0
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
            plate_wells.append(plate_well)

            if len(blank_row_ids) == 0:
                # ID for this row is next negative number, causing insert.
                id_to_insert = id_to_insert - 1
                id = id_to_insert
                inserted_count += 1
            else:
                # ID for this row is one of the empty rows.
                id = int(blank_row_ids.pop(0))
                updated_count += 1
            # Make a row for each field in the model.
            record = model.dict()
            for field in list(record.keys()):
                # Ignore the ID from the model since it is of indeterminate value at this point.
                if field == "ID":
                    continue
                # Certain fields on the row come from the current head row field values.
                if field == "ProteinName":
                    value = protein
                elif field == "DropVolume":
                    value = drop_volume
                else:
                    value = record[field]
                fields.append(
                    {
                        "id": str(id),
                        "field": field,
                        "value": value,
                    }
                )

        await self.soakdb3_dataface_client.update_body_fields(  # type: ignore
            visitid,
            fields,
        )

        return {
            "updated_count": updated_count,
            "inserted_count": inserted_count,
            "skipped_count": skipped_count,
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
