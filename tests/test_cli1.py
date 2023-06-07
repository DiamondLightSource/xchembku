import asyncio
import logging
import os
import subprocess
import time
from typing import Optional

from dls_utilpack.describe import describe

# Base class for the tester.
from tests.base import Base
from xchembku_api.datafaces.context import Context as ClientContext

# Object managing datafaces.
from xchembku_api.models.crystal_plate_filter_model import CrystalPlateFilterModel
from xchembku_api.models.crystal_plate_model import CrystalPlateModel

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestCli1Sqlite:
    """
    Test that we can start the service (which uses sqlite) via the command line and talk to it.
    """

    def test(self, constants, logging_setup, output_directory):

        configuration_file = "tests/configurations/service_sqlite.yaml"
        Cli1Tester(configuration_file).main(
            constants,
            configuration_file,
            output_directory,
        )


# ----------------------------------------------------------------------------------------
class TestCli1Mysql:
    """
    Test that we can start the service (which uses mysql) via the command line and talk to it.
    """

    def test(self, constants, logging_setup, output_directory):

        configuration_file = "tests/configurations/service_mysql.yaml"
        Cli1Tester(configuration_file).main(
            constants,
            configuration_file,
            output_directory,
        )


# ----------------------------------------------------------------------------------------
class Cli1Tester(Base):
    """
    Class to test the dataface.
    """

    def __init__(self, configuration_file):
        Base.__init__(self)

        self.__configuration_file = configuration_file

    async def _main_coroutine(self, constants, output_directory):
        """ """

        # Command to run the service.
        xchembku_server_cli = [
            "python",
            "-m",
            "xchembku_cli.main",
            "service",
            "--verbose",
            "--configuration",
            self.__configuration_file,
        ]

        # Let the output_directory symbol be replaced in the multiconf.
        os.environ["output_directory"] = output_directory

        # Launch the service as a process.
        logger.debug(f"launching subprocess {' '.join(xchembku_server_cli)}")
        process = subprocess.Popen(
            xchembku_server_cli,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            # Read the same configuration which the service process reads.
            multiconf_object = self.get_multiconf()
            multiconf_dict = await multiconf_object.load()

            # Get a client context to the server in the process we just started.
            xchembku_specification = multiconf_dict["xchembku_dataface_specification"]
            xchembku_client_context = ClientContext(xchembku_specification)
            async with xchembku_client_context as xchembku_client:
                # Wait until process is able to give a non-exceptional health report.
                start_time = time.time()
                max_seconds = 5.0
                while True:
                    # Try to check the health.
                    health = await xchembku_client.client_report_health()

                    # Check if health report contains an exception.
                    exception = health.get("exception")
                    if exception is None:
                        logger.debug(describe("health", health))
                        # Continue with test if no exception.
                        break

                    logger.debug(f"[CONNRETRY] retrying after {exception}")

                    if process.poll() is not None:
                        raise RuntimeError(
                            "server apprently died without being able to give a health check"
                        )

                    # Too much time has elapsed?
                    if time.time() - start_time > max_seconds:
                        raise RuntimeError(
                            f"server not answering within {max_seconds} seconds"
                        )

                    await asyncio.sleep(1.0)

                # Interact with the server now that it's up.
                visit = "cm00001-1"
                models = []
                models.append(
                    CrystalPlateModel(
                        formulatrix__plate__id=10,
                        barcode="xyz1",
                        visit=visit,
                    )
                )
                models.append(
                    CrystalPlateModel(
                        formulatrix__plate__id=20,
                        barcode="xyz2",
                        visit=visit,
                    )
                )
                models.append(
                    CrystalPlateModel(
                        formulatrix__plate__id=30,
                        barcode="xyz3",
                        visit=visit,
                    )
                )

                await xchembku_client.upsert_crystal_plates(models)

                # Check the filtered queries.
                await self.__check(
                    xchembku_client,
                    CrystalPlateFilterModel(),
                    3,
                    "all",
                )

                await xchembku_client.client_shutdown()
        finally:
            try:
                # Wait for the process to finish and get the output.
                stdout_bytes, stderr_bytes = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                # Timeout happens when client dies but server hasn't been told to shutdown.
                process.kill()
                stdout_bytes, stderr_bytes = process.communicate()

            # Get the return code of the process
            return_code = process.returncode
            logger.debug(f"server return_code is {return_code}")

            if len(stderr_bytes) > 0:
                logger.debug(
                    f"================================== server stderr is:\n{stderr_bytes.decode()}"
                )
            if len(stdout_bytes) > 0:
                logger.debug(
                    f"================================== server stdout is:\n{stdout_bytes.decode()}"
                )
            if len(stderr_bytes) > 0 or len(stdout_bytes) > 0:
                logger.debug("================================== end of server output")

        assert return_code == 0

    # ----------------------------------------------------------------------------------------

    async def __check(
        self,
        dataface,
        filter: CrystalPlateFilterModel,
        expected: int,
        note: str,
        formulatrix__plate__id: Optional[int] = None,
    ):
        """ """

        crystal_plate_models = await dataface.fetch_crystal_plates(filter)

        assert len(crystal_plate_models) == expected, note

        if formulatrix__plate__id is not None:
            assert (
                crystal_plate_models[0].formulatrix__plate__id == formulatrix__plate__id
            ), f"{note} formulatrix__plate__id"

        return crystal_plate_models
