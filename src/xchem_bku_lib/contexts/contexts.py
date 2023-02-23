# Use standard logging in this module.
import logging

import yaml

# Exceptions.
from xchembku_api.exceptions import NotFound

# Class managing list of things.
from xchembku_api.things import Things

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------


class Contexts(Things):
    """
    Context loader.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        if not isinstance(specification, dict):
            with open(specification, "r") as yaml_stream:
                specification = yaml.safe_load(yaml_stream)

        xchembku_context_class = self.lookup_class(specification["type"])

        try:
            xchembku_context_object = xchembku_context_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build xchembku_context object for type %s"
                % (xchembku_context_class)
            ) from exception

        return xchembku_context_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "xchembku_lib.xchembku_contexts.classic":
            from xchembku_lib.contexts.classic import Classic

            return Classic

        raise NotFound(
            "unable to get xchembku_context class for type %s" % (class_type)
        )
