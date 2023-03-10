import uuid
from typing import Optional

from pydantic import BaseModel


class CrystalWellModel(BaseModel):
    """
    Model containing well information.

    Typically this structure is populated and transmitted by the rockingest package.
    """

    uuid: str
    filename: str
    target_position_x: Optional[int] = None
    target_position_y: Optional[int] = None

    # TODO: Add proper pydantic date parsing/valiation to CREATED_ON fields.
    created_on: Optional[str] = None

    def __init__(self, **kwargs):
        # Automatically cook up a uuid if it's not provided to the constructor.
        if "uuid" not in kwargs:
            kwargs["uuid"] = str(uuid.uuid4())
        super().__init__(**kwargs)
