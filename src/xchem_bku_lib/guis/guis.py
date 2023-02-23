# Use standard logging in this module.
import logging

# Exceptions.
from xchembku_api.exceptions import NotFound

# Class managing list of things.
from xchembku_api.things import Things

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------
__default_xchembku_gui = None


def xchembku_guis_set_default(xchembku_gui):
    global __default_xchembku_gui
    __default_xchembku_gui = xchembku_gui


def xchembku_guis_get_default():
    global __default_xchembku_gui
    if __default_xchembku_gui is None:
        raise RuntimeError("xchembku_guis_get_default instance is None")
    return __default_xchembku_gui


def xchembku_guis_has_default():
    global __default_xchembku_gui
    return __default_xchembku_gui is not None


# -----------------------------------------------------------------------------------------


class Guis(Things):
    """
    List of available xchembku_guis.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        xchembku_gui_class = self.lookup_class(specification["type"])

        try:
            xchembku_gui_object = xchembku_gui_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build xchembku_gui object for type %s"
                % (xchembku_gui_class)
            ) from exception

        return xchembku_gui_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "xchembku_lib.xchembku_guis.aiohttp":
            from xchembku_lib.guis.aiohttp import Aiohttp

            return Aiohttp

        raise NotFound("unable to get xchembku_gui class for type %s" % (class_type))
