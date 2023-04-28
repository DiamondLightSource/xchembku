import logging
from typing import Tuple

# Base class for generic things.
from dls_utilpack.thing import Thing

# Types.
from xchembku_api.crystal_plate_objects.constants import ThingTypes

logger = logging.getLogger(__name__)

thing_type = ThingTypes.SWISS3


class Swiss3(Thing):
    """ """

    __MICRONS_PER_PIXEL_X = 2.837
    __WELL_COUNT = 288

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None):
        Thing.__init__(self, thing_type, specification)

    # ----------------------------------------------------------------------------------------
    def get_well_count(self) -> int:
        return self.__WELL_COUNT

    # ----------------------------------------------------------------------------------------
    def convert_pixel_to_micron(self, pixel: Tuple[int, int]) -> Tuple[float, float]:
        return (
            pixel[0] * self.__MICRONS_PER_PIXEL_X,
            pixel[1] * self.__MICRONS_PER_PIXEL_X,
        )
