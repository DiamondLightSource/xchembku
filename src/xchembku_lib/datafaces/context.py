import logging

# Base class for an asyncio server context.
from dls_utilpack.server_context_base import ServerContextBase

# Things created in the context.
from xchembku_lib.datafaces.datafaces import Datafaces

logger = logging.getLogger(__name__)


thing_type = "xchembku_lib.xchembku_datafaces.context"


class Context(ServerContextBase):
    """
    Asyncio context for a xchembku_dataface server object.
    On entering, it creates the object according to the specification (a dict).
    If configured, it starts the server as a coroutine, thread or process.
    On exiting, it commands the server to shut down.

    The enter and exit methods are exposed for use during testing.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification):
        ServerContextBase.__init__(self, thing_type, specification)

    # ----------------------------------------------------------------------------------------
    async def aenter(self):
        """ """

        # Build the object according to the specification.
        self.server = Datafaces().build_object(self.specification())

        # If there is more than one collector, the last one defined will be the default.
        # collectors_set_default(self.server)

        if self.context_specification.get("start_as") == "coro":
            await self.server.activate_coro()

        elif self.context_specification.get("start_as") == "thread":
            await self.server.start_thread()

        elif self.context_specification.get("start_as") == "process":
            await self.server.start_process()

    # ----------------------------------------------------------------------------------------
    async def aexit(self, type=None, value=None, traceback=None):
        """
        Asyncio context exit.

        Stop service if one was started and releases any client resources.
        """
        logger.debug(f"[DISSHU] {thing_type} aexit")

        if self.server is not None:
            if self.context_specification.get("start_as") == "process":
                # The server associated with this context is running?
                if await self.is_process_alive():
                    logger.debug(f"[DISSHU] {thing_type} calling client_shutdown")
                    # Put in request to shutdown the server.
                    await self.server.client_shutdown()

            if self.context_specification.get("start_as") == "coro":
                await self.server.direct_shutdown()
