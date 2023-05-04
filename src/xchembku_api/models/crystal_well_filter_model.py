from enum import Enum
from typing import Optional

from pydantic import BaseModel


class CrystalWellFilterSortbyEnum(str, Enum):
    POSITION = "position"
    NUMBER_OF_CRYSTALS = "number_of_crystals"


class CrystalWellFilterModel(BaseModel):
    """
    Model containing crystal well query filter.
    """

    filename_pattern: Optional[str] = None
    visit: Optional[str] = None
    barcode: Optional[str] = None
    anchor: Optional[str] = None
    limit: Optional[int] = None
    sortby: Optional[CrystalWellFilterSortbyEnum] = None
    direction: Optional[int] = None
    is_decided: Optional[bool] = None
    is_usable: Optional[bool] = None
