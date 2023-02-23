# Use standard logging in this module.
import logging

# Exceptions.
from xchembku_api.exceptions import NotFound

# Class managing list of things.
from xchembku_api.things import Things

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------------------


class Datafaces(Things):
    """
    List of available xchembku_datafaces.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        xchembku_dataface_class = self.lookup_class(specification["type"])

        try:
            xchembku_dataface_object = xchembku_dataface_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build xchembku_dataface object for type %s"
                % (xchembku_dataface_class)
            ) from exception

        return xchembku_dataface_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "xchembku_lib.xchembku_datafaces.aiohttp":
            from xchembku_lib.datafaces.aiohttp import Aiohttp

            return Aiohttp

        elif class_type == "xchembku_lib.xchembku_datafaces.aiosqlite":
            from xchembku_lib.datafaces.aiosqlite import Aiosqlite

            return Aiosqlite

        raise NotFound(
            "unable to get xchembku_dataface class for type %s" % (class_type)
        )
