import logging

# Base class for the tester.
from tests.base_context_tester import BaseContextTester
from xchembku_api.databases.constants import CrystalWellFieldnames, Tablenames

# Object managing datafaces.
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default

# Context creator.
from xchembku_lib.contexts.contexts import Contexts

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestDataface:
    def test_dataface_multiconf(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/multiconf.yaml"
        DatafaceTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class DatafaceTester(BaseContextTester):
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
                        CrystalWellFieldnames.FILENAME: "x",
                        CrystalWellFieldnames.TARGET_POSITION_X: "1",
                        CrystalWellFieldnames.TARGET_POSITION_Y: "2",
                    }
                ],
            )

            all_sql = f"SELECT * FROM {Tablenames.CRYSTAL_WELLS}"
            records = await dataface.query(all_sql)

            assert len(records) == 1
            assert records[0][CrystalWellFieldnames.FILENAME] == "x"
            assert records[0][CrystalWellFieldnames.TARGET_POSITION_X] == 1
            assert records[0][CrystalWellFieldnames.TARGET_POSITION_Y] == 2

            # ----------------------------------------------------------------
            # Now try an update.
            record = {
                CrystalWellFieldnames.WELL_CENTER_X: 123,
                CrystalWellFieldnames.WELL_CENTER_Y: 456,
            }

            subs = [1]
            result = await dataface.update(
                Tablenames.CRYSTAL_WELLS,
                record,
                f"{CrystalWellFieldnames.AUTOID} = ?",
                subs=subs,
                why="test update",
            )

            assert result["count"] == 1
            records = await dataface.query(all_sql)

            assert len(records) == 1
            assert records[0][CrystalWellFieldnames.WELL_CENTER_X] == 123
            assert records[0][CrystalWellFieldnames.WELL_CENTER_Y] == 456
