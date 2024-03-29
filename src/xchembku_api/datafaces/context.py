import logging

# Base class.
from dls_utilpack.client_context_base import ClientContextBase

# Things created in the context.
from xchembku_api.datafaces.datafaces import Datafaces, xchembku_datafaces_set_default

logger = logging.getLogger(__name__)


class Context(ClientContextBase):
    """
    Client context for a xchembku_dataface object.
    On entering, it creates the object according to the specification (a dict).
    On exiting, it closes client connection.

    The aenter and aexit methods are exposed for use by an enclosing context and the base class.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification):
        ClientContextBase.__init__(self, specification)

    # ----------------------------------------------------------------------------------------
    async def aenter(self):
        """ """

        # Build the object according to the specification.
        self.interface = Datafaces().build_object(self.specification)

        # If there is more than one dataface, the last one defined will be the default.
        xchembku_datafaces_set_default(self.interface)

        # Open client session to the service or direct connection.
        await self.interface.open_client_session()

        # For convenience, return the object which is the client interface.
        return self.interface

    # ----------------------------------------------------------------------------------------
    async def aexit(self):
        """ """
        if self.interface is not None:
            # Close client session to the service or direct connection.
            await self.interface.close_client_session()

            # Clear the global variable.  Important between pytests.
            xchembku_datafaces_set_default(None)
