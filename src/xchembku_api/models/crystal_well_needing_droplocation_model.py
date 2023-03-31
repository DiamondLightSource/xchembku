import uuid
from typing import Optional

from pydantic import BaseModel


class CrystalWellNeedingDroplocationModel(BaseModel):
    """
    Model containing well information formed from a composite query of droplocation information.

    Typically this structure is returned by queries.
    """

    # Stuff from the original record.
    uuid: str
    filename: str
    created_on: str

    # Stuff from the autolocation.
    auto_target_position_x: Optional[int] = None
    auto_target_position_y: Optional[int] = None
    well_centroid_x: Optional[int] = None
    well_centroid_y: Optional[int] = None

    # Stuff from the droplocation.
    is_valid: Optional[bool] = None
    confirmed_target_position_x: Optional[int] = None
    confirmed_target_position_y: Optional[int] = None
