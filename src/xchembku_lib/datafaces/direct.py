import logging

from xchembku_lib.datafaces.direct_base import DirectBase
from xchembku_lib.datafaces.direct_crystal_plates import DirectCrystalPlates
from xchembku_lib.datafaces.direct_crystal_well_autolocations import (
    DirectCrystalWellAutolocations,
)
from xchembku_lib.datafaces.direct_crystal_well_droplocations import (
    DirectCrystalWellDroplocations,
)
from xchembku_lib.datafaces.direct_crystal_wells import DirectCrystalWells

logger = logging.getLogger(__name__)


class Direct(
    DirectCrystalPlates,
    DirectCrystalWells,
    DirectCrystalWellAutolocations,
    DirectCrystalWellDroplocations,
    DirectBase,
):
    """ """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None):
        DirectBase.__init__(self, specification)
