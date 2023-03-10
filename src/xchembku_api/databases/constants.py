# Fieldnames common to all databases.
from dls_normsql.constants import CommonFieldnames


class Types:
    NORMSQL = "xchembku_lib.xchembku_databases.normsql"


# ----------------------------------------------------------------------------------------
class CrystalWellFieldnames:
    FILENAME = "filename"
    ERROR = "error"
    WIDTH = "width"
    HEIGHT = "height"
    WELL_CENTER_X = "well_center_x"
    WELL_CENTER_Y = "well_center_y"
    TARGET_POSITION_X = "target_position_x"
    TARGET_POSITION_Y = "target_position_y"
    PLATE_TYPE = "plate_type"
    CRYSTAL_PROBABILITY = "crystal_probability"
    NUMBER_OF_CRYSTALS = "number_of_crystals"
    IS_DROP = "is_drop"
    IS_USABLE = "is_usable"
