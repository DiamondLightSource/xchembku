import uuid
from typing import Optional

from pydantic import BaseModel


class CrystalWellModel(BaseModel):
    """
    Model containing well information.

    Typically this structure is populated and transmitted by the rockingest package.
    """

    uuid: str

    # This is the plate on which the well resides.
    crystal_plate_uuid: str

    # This is the well's position on the plate, such as A01_1, A01_2, etc.
    # TODO: Enforce crystal_well.position unique among wells in plate.
    position: str

    # This is the filename containing the well's image.
    filename: str

    # This is the size of the well's image.
    # Optional for now to avoid having to refactor all tests to include it on the constructur.
    # TODO: Make crystal_well_model width and height not optional.
    width: Optional[int] = None
    height: Optional[int] = None

    # This is the error reading and parsing the image file, if any.
    error: Optional[str]

    # TODO: Add proper pydantic date parsing/valiation to CREATED_ON fields.
    created_on: Optional[str] = None

    def __init__(self, **kwargs):
        # Automatically cook up a uuid if it's not provided to the constructor.
        if "uuid" not in kwargs:
            kwargs["uuid"] = str(uuid.uuid4())
        super().__init__(**kwargs)
