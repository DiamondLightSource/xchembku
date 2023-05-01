import logging
from typing import Dict, Optional, Tuple

# Base class for generic things.
from dls_utilpack.describe import describe
from dls_utilpack.thing import Thing

# Types.
from xchembku_api.crystal_plate_objects.constants import ThingTypes

logger = logging.getLogger(__name__)

thing_type = ThingTypes.SWISS3


class Swiss3(Thing):
    """ """

    __MICRONS_PER_PIXEL_X = 2.837
    __MICRONS_PER_PIXEL_Y = 2.837
    __WELL_COUNT = 288

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None):
        Thing.__init__(self, thing_type, specification)

    # ----------------------------------------------------------------------------------------
    def get_well_count(self) -> int:
        return self.__WELL_COUNT

    # ----------------------------------------------------------------------------------------
    def compute_drop_location_microns(
        self,
        crystal_well_record: Dict,
    ) -> Tuple[Optional[int], Optional[int]]:

        logger.debug(describe("crystal_well_record", crystal_well_record))
        if crystal_well_record.get("confirmed_target_x") is None:
            return (None, None)
        if crystal_well_record.get("confirmed_target_y") is None:
            return (None, None)

        x = int(
            0.5
            + self.__MICRONS_PER_PIXEL_X
            * (
                crystal_well_record["confirmed_target_x"]
                - crystal_well_record["well_centroid_x"]
            )
        )
        y = int(
            0.5
            + self.__MICRONS_PER_PIXEL_Y
            * (
                crystal_well_record["confirmed_target_y"]
                - crystal_well_record["well_centroid_y"]
            )
        )

        return (x, y)
