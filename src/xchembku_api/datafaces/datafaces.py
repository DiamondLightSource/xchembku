# Use standard logging in this module.
import logging

# Class managing list of things.
from dls_utilpack.things import Things

# Types.
from xchembku_api.datafaces.constants import Types

# Exceptions.
from xchembku_api.exceptions import NotFound

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------
__default_xchembku_dataface = None


def xchembku_datafaces_set_default(xchembku_dataface):
    global __default_xchembku_dataface
    __default_xchembku_dataface = xchembku_dataface


def xchembku_datafaces_get_default():
    global __default_xchembku_dataface
    if __default_xchembku_dataface is None:
        raise RuntimeError("xchembku_datafaces_get_default instance is None")
    return __default_xchembku_dataface


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

        if class_type == Types.AIOHTTP:
            from xchembku_api.datafaces.aiohttp import Aiohttp

            return Aiohttp

        if class_type == Types.DIRECT:
            from xchembku_lib.datafaces.direct import Direct

            return Direct

        raise NotFound(
            "unable to get xchembku_dataface class for type %s" % (class_type)
        )
