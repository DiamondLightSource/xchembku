import uuid

from pydantic import BaseModel


class WellModel(BaseModel):
    """
    Model containing well information.

    Typically this structure is populated and transmitted by the rockingest package.
    """

    uuid: str
    filename: str

    def __init__(self, filename: str):
        super().__init__(filename=filename, uuid=str(uuid.uuid4()))
