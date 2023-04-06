import uuid
from typing import List, Optional, Tuple

from pydantic import BaseModel


class CrystalWellAutolocationModel(BaseModel):
    """
    Model containing crystal well autolocation information.

    Typically this structure is populated and transmitted by the chimpflow.
    """

    uuid: str
    crystal_well_uuid: Optional[str] = None
    drop_detected: Optional[bool] = None
    auto_target_position_x: Optional[int] = None
    auto_target_position_y: Optional[int] = None
    well_centroid_x: Optional[int] = None
    well_centroid_y: Optional[int] = None
    number_of_crystals: Optional[int] = None
    crystal_coordinates: Optional[List[Tuple[int, int]]] = None

    # TODO: Add proper pydantic date parsing/valiation to CREATED_ON fields.
    created_on: Optional[str] = None

    def __init__(self, **kwargs):
        # Automatically cook up a uuid if it's not provided to the constructor.
        if "uuid" not in kwargs:
            kwargs["uuid"] = str(uuid.uuid4())
        super().__init__(**kwargs)

    # For temporary reference, this is what xchem_chimp was doing to send to echolocator database:
    # request_dict[ImageFieldnames.FILENAME] = str(im_path)
    # if output_dict["drop_detected"] is True:
    #     request_dict[ImageFieldnames.IS_DROP] = True
    #     echo_y, echo_x = output_dict["echo_coordinate"][0]
    #     request_dict[ImageFieldnames.TARGET_POSITION_Y] = int(echo_y)
    #     request_dict[ImageFieldnames.TARGET_POSITION_X] = int(echo_x)
    #     centroid_y, centroid_x = output_dict["well_centroid"]
    #     request_dict[ImageFieldnames.WELL_CENTER_Y] = int(centroid_y)
    #     request_dict[ImageFieldnames.WELL_CENTER_X] = int(centroid_x)
    #     num_xtals = len(output_dict["xtal_coordinates"])
    #     request_dict[ImageFieldnames.NUMBER_OF_CRYSTALS] = int(num_xtals)
    #     logging.info(f"output_dict is\n{describe('output_dict', output_dict)}")
    # else:
    #     request_dict[ImageFieldnames.IS_DROP] = False
    #     request_dict[ImageFieldnames.IS_USABLE] = False
    # logging.info(f"Sending request for {im_path} to EchoLocator database")
    # asyncio.run(self.send_item_to_echolocator(request_dict))
