import asyncio
import logging
import multiprocessing
import os

import pytest

# Configurator.
from xchembku_lib.configurators.configurators import (
    Configurators,
    xchembku_configurators_set_default,
)

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class BaseContextTester:
    """
    This is a base class for tests which use Context.
    """

    def __init__(self):
        self.tasks_execution_outputs = {}
        self.residuals = ["stdout.txt", "stderr.txt", "main.log"]

    def main(self, constants, configuration_file, output_directory):
        """
        This is the main program which calls the test using asyncio.
        """

        # Save these for when the configuration is loaded.
        self.__configuration_file = configuration_file
        self.__output_directory = output_directory

        multiprocessing.current_process().name = "main"

        # self.__blocked_event = asyncio.Event()

        failure_message = None
        try:
            # Run main test in asyncio event loop.
            asyncio.run(self._main_coroutine(constants, output_directory))

        except Exception as exception:
            logger.exception(
                "unexpected exception in the test method", exc_info=exception
            )
            failure_message = str(exception)

        if failure_message is not None:
            pytest.fail(failure_message)

    # ----------------------------------------------------------------------------------------
    def get_configurator(self):

        xchembku_configurator = Configurators().build_object(
            {
                "type": "xchembku_lib.xchembku_configurators.yaml",
                "type_specific_tbd": {"filename": self.__configuration_file},
            }
        )

        # For convenience, always do these replacement.
        xchembku_configurator.substitute(
            {"output_directory": self.__output_directory}
        )

        # Add various things from the environment into the configurator.
        xchembku_configurator.substitute(
            {
                "CWD": os.getcwd(),
                "PYTHONPATH": os.environ.get("PYTHONPATH", "PYTHONPATH"),
            }
        )

        # Set the global value of our configurator which might be used in other modules.
        xchembku_configurators_set_default(xchembku_configurator)

        return xchembku_configurator
