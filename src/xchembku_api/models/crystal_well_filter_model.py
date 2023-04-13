from typing import Optional

from pydantic import BaseModel


class CrystalWellFilterModel(BaseModel):
    """
    Model containing crystal well query filter.
    """

    filename_pattern: Optional[str] = None
    visit: Optional[str] = None
    barcode: Optional[str] = None
    anchor: Optional[str] = None
    limit: Optional[int] = None
    direction: Optional[int] = None
    is_decided: Optional[bool] = None
    is_usable: Optional[bool] = None
