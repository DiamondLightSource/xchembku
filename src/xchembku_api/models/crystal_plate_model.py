import uuid
from typing import Optional

from pydantic import BaseModel


class CrystalPlateModel(BaseModel):
    """
    Model containing plate information.

    Typically this structure is populated and transmitted by the rockminer package.
    """

    uuid: str
    # ID from the Plate table.
    formulatrix__plate__id: int
    barcode: str
    visit: str

    # TODO: Add proper pydantic date parsing/valiation to CREATED_ON fields.
    created_on: Optional[str] = None

    def __init__(self, **kwargs):
        # Automatically cook up a uuid if it's not provided to the constructor.
        if "uuid" not in kwargs:
            kwargs["uuid"] = str(uuid.uuid4())
        super().__init__(**kwargs)
