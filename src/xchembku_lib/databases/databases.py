# Use standard logging in this module.
import logging

# Class managing list of things.
from dls_utilpack.things import Things

# Types.
from xchembku_api.databases.constants import Types

# Exceptions.
from xchembku_api.exceptions import NotFound

logger = logging.getLogger(__name__)


class Databases(Things):
    """
    List of available databases.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        database_class = self.lookup_class(specification["type"])

        try:
            database_object = database_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build database object for type %s" % (database_class)
            ) from exception

        return database_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """
        Given the class type as string, return a class object.
        """

        if class_type == Types.NORMSQL:
            from xchembku_lib.databases.normsql import Normsql

            return Normsql

        raise NotFound("unable to get database class for type %s" % (class_type))
