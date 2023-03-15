import logging

# Base class for an asyncio context
from xchembku_lib.contexts.base import Base as ContextBase

# Things created in the context.
from xchembku_lib.datafaces.datafaces import Datafaces

logger = logging.getLogger(__name__)


thing_type = "xchembku_lib.xchembku_datafaces.context"


class Context(ContextBase):
    """
    Asyncio context for a xchembku_dataface server object.
    On entering, it creates the object according to the specification (a dict).
    If configured, it starts the server as a coroutine, thread or process.
    On exiting, it commands the server to shut down.

    The enter and exit methods are exposed for use during testing.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification):
        ContextBase.__init__(self, thing_type, specification)

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
    async def aexit(self):
        """ """

        if self.server is not None:
            if self.context_specification.get("start_as") == "process":
                # Put in request to shutdown the server.
                await self.server.client_shutdown()

            if self.context_specification.get("start_as") == "coro":
                await self.server.direct_shutdown()
