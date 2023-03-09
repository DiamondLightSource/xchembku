from typing import List, Tuple

from pydantic import BaseModel


class WellGeometryModel(BaseModel):
    """
    Model containing well geometry.

    Typically this structure is populated and transmitted by the chimpflow.
    """

    well_uuid: str
    drop_detected: bool = None
    target_position_x: int = None
    target_position_y: int = None
    well_centroid_x: int = None
    well_centroid_y: int = None
    number_of_crystals: int = None
    crystal_coordinates: List[Tuple[int, int]] = None

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