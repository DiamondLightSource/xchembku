# Use standard logging in this module.
import logging

# Exceptions.
from xchembku_api.exceptions import NotFound

# Class managing list of things.
from xchembku_api.things import Things

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------
__default_composer = None


def xchembku_composers_set_default(composer):
    global __default_composer
    __default_composer = composer


def xchembku_composers_get_default():
    global __default_composer
    if __default_composer is None:
        raise RuntimeError("xchembku_composers_get_default instance is None")
    return __default_composer


def xchembku_composers_has_default():
    global __default_composer
    return __default_composer is not None


# -----------------------------------------------------------------------------------------


class Composers(Things):
    """
    List of available xchembku_composers.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        composer_class = self.lookup_class(specification["type"])

        try:
            composer_object = composer_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build composer object for type %s" % (composer_class)
            ) from exception

        return composer_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "xchembku_lib.xchembku_composers.html":
            from xchembku_lib.composers.html import Html

            return Html

        elif class_type == "xchembku_lib.xchembku_composers.text":
            from xchembku_lib.composers.text import Text

            return Text

        raise NotFound("unable to get composer class for type %s" % (class_type))
