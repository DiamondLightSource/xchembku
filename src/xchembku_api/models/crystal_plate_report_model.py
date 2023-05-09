from typing import Optional

from pydantic import BaseModel


class CrystalPlateReportModel(BaseModel):
    """
    Model containing plate information.

    Typically this structure is populated and transmitted by the rockminer package.
    """

    uuid: str
    # ID from the Plate table.
    formulatrix__plate__id: int
    # Name from the formulatrix "experiment" tree node.
    formulatrix__experiment__name: Optional[str]
    # Directory stem where wells were mined from.
    # Also used by echolocator to format the export csv filename.
    rockminer_collected_stem: Optional[str] = None
    # The 4-letter barcode.
    barcode: str
    # The visit gleaned from the Formulatrix database.
    visit: str
    # A string which allows the CrytsalPlateObjects factory to make an instance.
    thing_type: str

    # TODO: Add proper pydantic date parsing/valiation to CREATED_ON fields.
    created_on: str

    # These are not in the database, but get returned from some queries.
    collected_count: int
    chimped_count: int
    undecided_count: int
    undecided_crystals_count: int
    decided_count: int
    decided_usable_count: int
    decided_unusable_count: int
    exported_count: int
    usable_unexported_count: int
