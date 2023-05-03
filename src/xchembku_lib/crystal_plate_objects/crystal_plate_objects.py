# Use standard logging in this module.
import logging
from typing import List

# Class managing list of things.
from dls_utilpack.things import Things

# Types which the CrystalPlateObjects factory can use to build an instance.
from xchembku_api.crystal_plate_objects.constants import ThingTypes

# Interface fulfilled by all CrystalPlateObject isntances.
from xchembku_api.crystal_plate_objects.interface import (
    Interface as CrystalPlateInterface,
)

# Exceptions.
from xchembku_api.exceptions import NotFound

logger = logging.getLogger(__name__)


class CrystalPlateObjects(Things):
    """
    List of available crystal plate object types.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def get_treenode_names(self) -> List[str]:
        """
        Returns list of all the Formulatrix treenode names which are interesting to soakdb3.

        Returns:
            List[str]: names
        """

        return list(self.__treenode_names_to_thing_type.keys())

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification) -> CrystalPlateInterface:
        """ """

        object_class = self.lookup_class(specification["type"])

        try:
            object_instance = object_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build object for type %s" % object_class
            ) from exception

        return object_instance

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """
        Given the class type as string, return a class object.
        """

        if class_type == ThingTypes.SWISS3:
            from xchembku_lib.crystal_plate_objects.swiss3 import Swiss3

            return Swiss3

        raise NotFound("unable to get class for type %s" % (class_type))
