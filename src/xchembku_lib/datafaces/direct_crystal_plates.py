import copy
import logging
from typing import Dict, List, Union

from dls_normsql.constants import CommonFieldnames

from xchembku_api.models.crystal_plate_filter_model import CrystalPlateFilterModel
from xchembku_api.models.crystal_plate_model import CrystalPlateModel
from xchembku_api.models.crystal_plate_report_model import CrystalPlateReportModel
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

        We don't insert the same formulatrix__plate__id twice.

        TODO: Find more efficient way to upsert_crystal_plates in batch.
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

        if why is None:
            why = "API fetch_crystal_plates"

        # Build the individual pieces of the SQL query.
        subs: List[Union[str, int]] = []
        orderby = self.__build_orderby(filter)
        where = self.__build_where(filter, subs)
        fields = self.__build_fields(filter)
        joins = self.__build_joins(filter)

        # Glue them together.
        main_query = "\nSELECT" + fields + joins + where + "\n" + orderby

        if filter.limit is not None:
            main_query += f"\nLIMIT {filter.limit}"

        records = await self.query(main_query, subs=subs, why=why)

        # Parse the records returned by sql into models.
        models = [CrystalPlateModel(**record) for record in records]

        return models

    # ----------------------------------------------------------------------------------------
    async def report_crystal_plates_serialized(
        self, filter: Dict, why=None
    ) -> List[Dict]:
        """
        Caller provides the filters for selecting which crystal plates.
        Returns records from the database.
        """

        # Get the models from the direct call.
        models = await self.report_crystal_plates(
            CrystalPlateFilterModel(**filter), why=why
        )

        # Serialize models into dicts to give to the response.
        records = [model.dict() for model in models]

        return records

    # ----------------------------------------------------------------------------------------
    async def report_crystal_plates(
        self, filter: CrystalPlateFilterModel, why=None
    ) -> List[CrystalPlateReportModel]:
        """
        Plates need a droplocation if they have an autolocation but no droplocation.
        """

        if why is None:
            why = "API report_crystal_plates"

        # Build the individual pieces of the SQL query.
        subs: List[Union[str, int]] = []
        orderby = self.__build_orderby(filter, is_for_report=True)
        where = self.__build_where(filter, subs, is_for_report=True)
        fields = self.__build_fields(filter, is_for_report=True)
        joins = self.__build_joins(filter, is_for_report=True)

        # Glue them together.
        main_query = "\nSELECT" + fields + joins + where + "\n" + orderby

        if filter.limit is not None:
            main_query += f"\nLIMIT {filter.limit}"

        records = await self.query(main_query, subs=subs, why=why)

        # Parse the records returned by sql into models.
        models = [CrystalPlateReportModel(**record) for record in records]

        return models

    # ----------------------------------------------------------------------------------------
    def __build_fields(
        self,
        filter: CrystalPlateFilterModel,
        is_for_report: bool = False,
    ) -> str:
        """
        Wells need a droplocation if they have an autolocation.
        """

        fields = ["crystal_plates.*"]

        if is_for_report:
            fields.append("COALESCE(collected.count, 0) AS collected_count")
            fields.append("COALESCE(chimped.count, 0) AS chimped_count")
            fields.append(
                "COALESCE(chimped.count, 0) - COALESCE(decided.count, 0) AS undecided_count"
            )
            fields.append("COALESCE(decided.count, 0) AS decided_count")
            fields.append("COALESCE(decided_usable.count, 0) AS decided_usable_count")
            fields.append(
                "COALESCE(decided.count, 0) - COALESCE(decided_usable.count, 0) AS decided_unusable_count"
            )
            fields.append("COALESCE(exported.count, 0) AS exported_count")
            fields.append(
                "COALESCE(decided_usable.count, 0) - COALESCE(exported.count, 0) AS usable_unexported_count"
            )
            fields.append(
                "COALESCE(undecided_crystals.count, 0) AS undecided_crystals_count"
            )

        return "\n  " + ",\n  ".join(fields)

    # ----------------------------------------------------------------------------------------
    def __build_joins(
        self,
        filter: CrystalPlateFilterModel,
        is_for_report: bool = False,
    ) -> str:
        """
        Wells need a droplocation if they have an autolocation.
        """

        joins = ["crystal_plates"]

        if is_for_report:
            all = "SELECT crystal_plate_uuid, COUNT(*) AS count FROM crystal_wells"
            chimped = f"{all} JOIN crystal_well_autolocations ON crystal_well_autolocations.crystal_well_uuid = crystal_wells.uuid"
            viewed = f"{all} JOIN crystal_well_droplocations ON crystal_well_droplocations.crystal_well_uuid = crystal_wells.uuid"
            both = (
                f"{all}"
                "\n  JOIN crystal_well_autolocations ON crystal_well_autolocations.crystal_well_uuid = crystal_wells.uuid"
                "\n  LEFT JOIN crystal_well_droplocations ON crystal_well_droplocations.crystal_well_uuid = crystal_wells.uuid"
                "\n  WHERE (number_of_crystals > 0) AND (is_usable is NULL) "
            )
            joins.append(
                f"LEFT JOIN ({all} GROUP BY crystal_plate_uuid) AS collected"
                f"\n    ON collected.crystal_plate_uuid = crystal_plates.uuid"
            )
            joins.append(
                f"LEFT JOIN ({chimped} GROUP BY crystal_plate_uuid) AS chimped"
                f"\n    ON chimped.crystal_plate_uuid = crystal_plates.uuid"
            )
            joins.append(
                f"LEFT JOIN ({viewed} WHERE (is_usable IS NOT NULL) GROUP BY crystal_plate_uuid) AS decided"
                f"\n    ON decided.crystal_plate_uuid = crystal_plates.uuid"
            )
            joins.append(
                f"LEFT JOIN ({viewed} WHERE (is_usable = True) GROUP BY crystal_plate_uuid) AS decided_usable"
                f"\n    ON decided_usable.crystal_plate_uuid = crystal_plates.uuid"
            )
            joins.append(
                f"LEFT JOIN ({viewed} WHERE (is_exported_to_soakdb3 = True) GROUP BY crystal_plate_uuid) AS exported"
                f"\n    ON exported.crystal_plate_uuid = crystal_plates.uuid"
            )
            joins.append(
                f"LEFT JOIN ({both} GROUP BY crystal_plate_uuid) AS undecided_crystals"
                f"\n    ON undecided_crystals.crystal_plate_uuid = crystal_plates.uuid"
            )

        return "\nFROM " + "\n  ".join(joins)

    # ----------------------------------------------------------------------------------------
    def __build_where(
        self,
        filter: CrystalPlateFilterModel,
        subs: List[Union[str, int]],
        is_for_report: bool = False,
    ) -> str:
        """
        Wells need a droplocation if they have an autolocation.
        """

        where = "WHERE"
        sql = ""

        if filter.uuid is not None:
            sql += f"\n{where} uuid = ?"
            subs.append(filter.uuid)
            where = "AND"

        if filter.visit is not None:
            sql += f"\n{where} visit = ?"
            subs.append(filter.visit)
            where = "AND"

        if filter.barcode is not None:
            sql += f"\n{where} barcode = ?"
            subs.append(filter.barcode)
            where = "AND"

        if filter.from_formulatrix__plate__id is not None:
            if filter.direction == -1:
                sql += f"\n{where} formulatrix__plate__id < ?"
            else:
                sql += f"\n{where} formulatrix__plate__id > ?"
            subs.append(filter.from_formulatrix__plate__id)
            where = "AND"

        if filter.needing_intervention is not None:
            if filter.needing_intervention is True:
                sql += "\n/* Those needing intervention. */"
                sql += f"\n{where} (undecided_crystals_count > 0 OR usable_unexported_count > 0)"
            else:
                sql += "\n/* Those NOT needing intervention. */"
                sql += f"\n{where} (undecided_crystals_count = 0 AND usable_unexported_count = 0)"

        return sql

    # ----------------------------------------------------------------------------------------
    def __build_orderby(
        self,
        filter: CrystalPlateFilterModel,
        is_for_report: bool = False,
    ) -> str:

        sql = ""

        sql_direction = "ASC"
        if filter.direction == -1:
            sql_direction = "DESC"

        order_by = f"crystal_plates.formulatrix__plate__id {sql_direction}"

        sql += f"ORDER BY {order_by}"

        return sql
