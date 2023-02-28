import asyncio

# Use standard logging in this module.
import logging

from dls_utilpack.global_signals import global_sigint

# Base class for cli subcommands.
from xchembku_cli.subcommands.base import ArgKeywords, Base

# Context creator.
from xchembku_lib.datafaces.context import Context

logger = logging.getLogger()


# --------------------------------------------------------------
class Service(Base):
    """
    Start one or more services and keep them running until ^C.
    """

    def __init__(self, args, mainiac):
        super().__init__(args)

    # ----------------------------------------------------------------------------------------
    def run(self):
        """ """

        # Run in asyncio event loop.
        asyncio.run(self.__run_coro())

    # ----------------------------------------------------------
    async def __run_coro(self):
        """"""

        # Load the configuration.
        xchembku_multiconf = self.get_multiconf(vars(self._args))
        configuration = await xchembku_multiconf.load()

        # Make a service context from the specification in the configuration.
        context = Context(configuration["xchembku_dataface_specification"])

        # Activate the signal handling.
        global_sigint.activate()

        # Open the context which starts the service process.
        async with context:
            while True:
                await asyncio.sleep(0.1)
                if global_sigint.count() > 0:
                    logger.info("control-C detected")
                    await context.server.direct_shutdown()
                    break

        global_sigint.deactivate()

    # ----------------------------------------------------------
    def add_arguments(parser):

        parser.add_argument(
            "--configuration",
            "-c",
            help="Configuration file.",
            type=str,
            metavar="yaml filename",
            default=None,
            dest=ArgKeywords.CONFIGURATION,
        )

        return parser
