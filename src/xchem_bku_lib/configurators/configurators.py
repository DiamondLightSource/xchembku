# Use standard logging in this module.
import logging
import os

# Utilities.
from dls_utilpack.callsign import callsign
from dls_utilpack.require import require

# Exceptions.
from xchembku_api.exceptions import NotFound

# Class managing list of things.
from xchembku_api.things import Things

# Environment variables with some extra functionality.
from xchembku_lib.envvar import Envvar

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------
__default_xchembku_configurator = None


def xchembku_configurators_set_default(xchembku_configurator):
    global __default_xchembku_configurator
    __default_xchembku_configurator = xchembku_configurator


def xchembku_configurators_get_default():
    global __default_xchembku_configurator
    if __default_xchembku_configurator is None:
        raise RuntimeError("xchembku_configurators_get_default instance is None")
    return __default_xchembku_configurator


def xchembku_configurators_has_default():
    global __default_xchembku_configurator
    return __default_xchembku_configurator is not None


# -----------------------------------------------------------------------------------------


class Configurators(Things):
    """
    Configuration loader.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        xchembku_configurator_class = self.lookup_class(
            require(f"{callsign(self)} specification", specification, "type")
        )

        try:
            xchembku_configurator_object = xchembku_configurator_class(
                specification
            )
        except Exception as exception:
            raise RuntimeError(
                "unable to instantiate xchembku_configurator object from module %s"
                % (xchembku_configurator_class.__module__)
            ) from exception

        return xchembku_configurator_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "xchembku_lib.xchembku_configurators.yaml":
            from xchembku_lib.configurators.yaml import Yaml

            return Yaml

        raise NotFound(
            "unable to get xchembku_configurator class for type %s" % (class_type)
        )

    # ----------------------------------------------------------------------------------------
    def build_object_from_environment(self, environ=None):

        # Get the explicit name of the config file.
        xchembku_configfile = Envvar(Envvar.XCHEMBKU_CONFIGFILE, environ=environ)

        # Config file is explicitly named?
        if xchembku_configfile.is_set:
            # Make sure the path exists.
            configurator_filename = xchembku_configfile.value
            if not os.path.exists(configurator_filename):
                raise RuntimeError(
                    f"unable to find {Envvar.XCHEMBKU_CONFIGFILE} {configurator_filename}"
                )
        # Config file is not explicitly named?
        else:
            raise RuntimeError(
                f"environment variable {Envvar.XCHEMBKU_CONFIGFILE} is not set"
            )

        xchembku_configurator = self.build_object(
            {
                "type": "xchembku_lib.xchembku_configurators.yaml",
                "type_specific_tbd": {"filename": configurator_filename},
            }
        )

        xchembku_configurator.substitute(
            {"configurator_directory": os.path.dirname(configurator_filename)}
        )

        return xchembku_configurator
