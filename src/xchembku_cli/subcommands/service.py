import argparse
import asyncio

# Use standard logging in this module.
import logging

from dls_utilpack.require import require

# Base class for cli subcommands.
from xchembku_cli.subcommands.base import ArgKeywords, Base

# Servbase context creator.
from xchembku_lib.datafaces.context import Context as XchembkuDatafaceContext

logger = logging.getLogger()


# --------------------------------------------------------------
class Service(Base):
    """
    Start single service and block until ^C or remotely requested shutdown.
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
        """
        Run the service as an asyncio coro.
        """

        # Load the configuration.
        multiconf_object = self.get_multiconf(vars(self._args))
        # Resolve the symbols and give configuration as a dict.
        multiconf_dict = await multiconf_object.load()

        # Get the specfication we want by keyword in the full configuration.
        specification = require(
            "configuration",
            multiconf_dict,
            "xchembku_dataface_specification",
        )

        # We need the context to always start the service as a coro.
        if "context" not in specification:
            specification["context"] = {}
        specification["context"]["start_as"] = "coro"

        # Make the xchembku service context from the specification in the configuration.
        context = XchembkuDatafaceContext(specification)

        # Open the xchembku context which starts the service process.
        async with context:
            # Wait for the coro to finish.
            await context.server.wait_for_shutdown()

    # ----------------------------------------------------------
    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """
        Add arguments for this subcommand.

        This is a static method called from the main program.

        Args:
            parser (argparse.ArgumentParser): Parser object which has been created already.

        """

        parser.add_argument(
            "--configuration",
            "-c",
            help="Configuration file.",
            type=str,
            metavar="filename.yaml",
            default=None,
            dest=ArgKeywords.CONFIGURATION,
        )

        return parser
