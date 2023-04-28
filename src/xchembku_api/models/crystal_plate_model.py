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
    # Directory stem where wells were mined from.
    # Also used by echolocator to format the export csv filename.
    rockminer_collected_stem: Optional[str] = None
    # The 4-letter barcode.
    barcode: str
    # The visit gleaned from the Formulatrix database.
    visit: str
    # A string which allows the CrytsalPlateObjects factory to make an instance.
    thing_type: Optional[str] = None

    # TODO: Add proper pydantic date parsing/valiation to CREATED_ON fields.
    created_on: Optional[str] = None

    def __init__(self, **kwargs):
        # Automatically cook up a uuid if it's not provided to the constructor.
        if "uuid" not in kwargs:
            kwargs["uuid"] = str(uuid.uuid4())
        super().__init__(**kwargs)
