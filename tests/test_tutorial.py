import json
import logging
import subprocess

# Base class for the tester.
from tests.base_context_tester import BaseContextTester
from xchembku_api.databases.constants import CrystalWellFieldnames, Tablenames

# Object managing datafaces.
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default

# Context creator.
from xchembku_lib.contexts.contexts import Contexts

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestTutorial:
    def test_dataface_multiconf(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/multiconf.yaml"
        TutorialTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class TutorialTester(BaseContextTester):
    """
    Class to test the dataface.
    """

    async def _main_coroutine(self, constants, output_directory):
        """ """

        xchembku_multiconf = self.get_multiconf()

        context_configuration = await xchembku_multiconf.load()
        xchembku_context = Contexts().build_object(context_configuration)

        async with xchembku_context:
            dataface = xchembku_datafaces_get_default()

            # Write one record.
            await dataface.insert(
                Tablenames.CRYSTAL_WELLS,
                [
                    {
                        CrystalWellFieldnames.FILENAME: "1.jpg",
                        CrystalWellFieldnames.TARGET_POSITION_X: 1,
                        CrystalWellFieldnames.TARGET_POSITION_Y: 2,
                    },
                    {
                        CrystalWellFieldnames.FILENAME: "2.jpg",
                        CrystalWellFieldnames.TARGET_POSITION_X: 3,
                        CrystalWellFieldnames.TARGET_POSITION_Y: 4,
                    },
                ],
            )

            # Run the tutorial and capture the output.

            command = ["python", "tests/tutorials/tutorial2.py"]
            process = subprocess.run(command, capture_output=True)
            if process.returncode != 0:
                stderr = process.stderr.decode().replace("\\n", "\n")
                logger.debug(f"stderr is:\n{stderr}")
                assert process.returncode == 0

            stdout = process.stdout.decode().replace("\\n", "\n")
            logger.debug(f"stdout is:\n{stdout}")
            try:
                result = json.loads(stdout)
                assert result["count"] == 1
            except Exception:
                assert False, "stdout is not json"

            # Check the tutorial ran.
            all_sql = f"SELECT * FROM {Tablenames.CRYSTAL_WELLS}"
            records = await dataface.query(all_sql)

            assert len(records) == 2
            assert records[0][CrystalWellFieldnames.FILENAME] == "1.jpg"
            assert records[0][CrystalWellFieldnames.TARGET_POSITION_X] == 1
            assert records[0][CrystalWellFieldnames.TARGET_POSITION_Y] == 2
