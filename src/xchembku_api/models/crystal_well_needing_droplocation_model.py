from typing import Optional

from pydantic import BaseModel


class CrystalWellNeedingDroplocationModel(BaseModel):
    """
    Model containing well information formed from a composite query of droplocation information.

    Typically this structure is returned by queries.
    """

    # Stuff from the original record.
    uuid: str
    crystal_plate_uuid: str
    position: str
    filename: str
    width: Optional[int]
    height: Optional[int]
    error: Optional[str]
    created_on: str

    # Stuff from the plate.
    visit: str
    crystal_plate_thing_type: str

    # Stuff from the autolocation.
    auto_target_x: Optional[int] = None
    auto_target_y: Optional[int] = None
    well_centroid_x: Optional[int] = None
    well_centroid_y: Optional[int] = None
    drop_detected: Optional[bool] = None
    number_of_crystals: Optional[int] = None

    # Stuff from the droplocation.
    crystal_well_droplocation_uuid: Optional[str] = None
    confirmed_target_x: Optional[int] = None
    confirmed_target_y: Optional[int] = None
    confirmed_microns_x: Optional[int] = None
    confirmed_microns_y: Optional[int] = None

    is_usable: Optional[bool] = None
