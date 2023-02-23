import logging

# Base class for generic things.
from xchembku_api.thing import Thing

# Class to do the work using prettytable.
from xchembku_lib.composers.prettyhelper import PrettyHelper

logger = logging.getLogger(__name__)

thing_type = "xchembku_lib.xchembku_composers.text"


class Text(Thing):
    """ """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None):
        Thing.__init__(self, thing_type, specification)

        self.__prettyhelper = PrettyHelper()
