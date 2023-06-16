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
    rockminer_collected_stem: Optional[str] = None

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
    is_exported_to_soakdb3: Optional[bool] = None

    def row_first_position(self):
        # A01a becomes 01Aa for purposes of sorting such that we get all letters in row 01 before any letters in row 02.
        # Within the same plate.
        return (
            self.rockminer_collected_stem
            + self.position[1:3]
            + self.position[0]
            + self.position[-1]
        )
