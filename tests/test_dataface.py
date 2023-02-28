import logging

# Base class for the tester.
from tests.base import Base
from xchembku_api.databases.constants import CrystalWellFieldnames

# Object managing datafaces.
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default

# Context creator.
from xchembku_lib.datafaces.context import Context as XchembkuDatafaceContext

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestDatafaceDirect:
    def test_dataface_multiconf(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/direct.yaml"
        DatafaceTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class TestDatafaceService:
    def test_dataface_multiconf(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/service.yaml"
        DatafaceTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class DatafaceTester(Base):
    """
    Class to test the dataface.
    """

    async def _main_coroutine(self, constants, output_directory):
        """ """

        xchembku_multiconf = self.get_multiconf()

        context_configuration = await xchembku_multiconf.load()
        xchembku_context = XchembkuDatafaceContext(
            context_configuration["xchembku_dataface_specification"]
        )

        async with xchembku_context:
            dataface = xchembku_datafaces_get_default()

            # Write one record.
            await dataface.originate_crystal_wells(
                [
                    {
                        CrystalWellFieldnames.FILENAME: "x",
                        CrystalWellFieldnames.TARGET_POSITION_X: "1",
                        CrystalWellFieldnames.TARGET_POSITION_Y: "2",
                    }
                ],
            )

            filters = []
            records = await dataface.fetch_crystal_wells_filenames()

            assert len(records) == 1
            assert records[0][CrystalWellFieldnames.FILENAME] == "x"
            assert records[0][CrystalWellFieldnames.TARGET_POSITION_X] == 1
            assert records[0][CrystalWellFieldnames.TARGET_POSITION_Y] == 2

            # ----------------------------------------------------------------
            # Now try an update.
            record = {
                CrystalWellFieldnames.AUTOID: records[0][CrystalWellFieldnames.AUTOID],
                CrystalWellFieldnames.WELL_CENTER_X: 123,
                CrystalWellFieldnames.WELL_CENTER_Y: 456,
            }

            result = await dataface.update_crystal_wells(
                [record],
                why="test update",
            )

            assert result["count"] == 1

            records = await dataface.fetch_crystal_wells_filenames()
            assert len(records) == 1
            assert records[0][CrystalWellFieldnames.WELL_CENTER_X] == 123
            assert records[0][CrystalWellFieldnames.WELL_CENTER_Y] == 456
