import logging

from dls_utilpack.callsign import callsign

# Base class.
from xchembku_api.context_base import ContextBase

# Things created in the context.
from xchembku_api.datafaces.datafaces import Datafaces, xchembku_datafaces_set_default

logger = logging.getLogger(__name__)


class Context(ContextBase):
    """
    Client context for a xchembku_dataface object.
    On entering, it creates the object according to the specification (a dict).
    On exiting, it closes client connection.

    The aenter and aexit methods are exposed for use by an enclosing context.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification):
        self.__specification = specification

    # ----------------------------------------------------------------------------------------
    async def aenter(self):
        """ """

        # Build the object according to the specification.
        self.interface = Datafaces().build_object(self.__specification)

        # If there is more than one dataface, the last one defined will be the default.
        xchembku_datafaces_set_default(self.interface)

        # Open client session to the service or direct connection.
        await self.interface.open_client_session()

    # ----------------------------------------------------------------------------------------
    async def aexit(self):
        """ """
        logger.debug(f"[ECHDON] {callsign(self)} in aexit")

        if self.interface is not None:
            logger.debug(
                f"[ECHDON] {callsign(self)} calling close_client_session on {callsign(self.interface)}"
            )
            # Close client session to the service or direct connection.
            await self.interface.close_client_session()
            logger.debug(f"[ECHDON] {callsign(self)} called close_client_session")

            # Clear the global variable.  Important between pytests.
            xchembku_datafaces_set_default(None)
