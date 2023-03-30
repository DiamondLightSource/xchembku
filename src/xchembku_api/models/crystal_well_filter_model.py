import uuid
from typing import List, Optional, Tuple

from pydantic import BaseModel


class CrystalWellFilterModel(BaseModel):
    """
    Model containing crystal well query filter.
    """

    anchor: Optional[str] = None
    limit: Optional[int] = None
    direction: Optional[int] = None
    is_confirmed: Optional[bool] = None
