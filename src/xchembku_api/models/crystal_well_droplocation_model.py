import uuid
from typing import Optional

from pydantic import BaseModel


class CrystalWellDroplocationModel(BaseModel):
    """
    Model containing crystal well droplocation information.

    Typically this structure is populated and transmitted by the chimpflow.
    """

    uuid: str
    crystal_well_uuid: Optional[str] = None
    confirmed_target_x: Optional[int] = None
    confirmed_target_y: Optional[int] = None
    confirmed_microns_x: Optional[int] = None
    confirmed_microns_y: Optional[int] = None
    is_usable: Optional[bool] = None

    # TODO: Add proper pydantic date parsing/valiation to CREATED_ON fields.
    created_on: Optional[str] = None

    def __init__(self, **kwargs):
        # Automatically cook up a uuid if it's not provided to the constructor.
        if "uuid" not in kwargs:
            kwargs["uuid"] = str(uuid.uuid4())
        super().__init__(**kwargs)
