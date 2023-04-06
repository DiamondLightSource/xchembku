from typing import Optional

from pydantic import BaseModel


class CrystalPlateFilterModel(BaseModel):
    """
    Model containing crystal plate query filter.
    """

    uuid: Optional[str] = None
    barcode: Optional[str] = None
    limit: Optional[int] = None
    direction: Optional[int] = None
