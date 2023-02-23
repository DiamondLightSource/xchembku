import logging

from xchembku_api.databases.constants import ImageFieldnames, Tablenames

# Object managing datafaces.
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default

# Context creator.
from xchembku_lib.contexts.contexts import Contexts

# Base class for the tester.
from tests.base_context_tester import BaseContextTester

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestDatafaceImage:
    def test_dataface_laptop(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/laptop.yaml"
        DatafaceImageTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class DatafaceImageTester(BaseContextTester):
    """
    Class to test the dataface.
    """

    async def _main_coroutine(self, constants, output_directory):
        """ """

        xchembku_configurator = self.get_configurator()

        context_configuration = await xchembku_configurator.load()
        xchembku_context = Contexts().build_object(context_configuration)

        async with xchembku_context:
            dataface = xchembku_datafaces_get_default()

            # Write one record.
            await dataface.insert(
                Tablenames.ROCKMAKER_IMAGES,
                [
                    {
                        ImageFieldnames.FILENAME: "x",
                        ImageFieldnames.TARGET_POSITION_X: "1",
                        ImageFieldnames.TARGET_POSITION_Y: "2",
                    }
                ],
            )

            all_sql = f"SELECT * FROM {Tablenames.ROCKMAKER_IMAGES}"
            records = await dataface.query(all_sql)

            assert len(records) == 1
            assert records[0][ImageFieldnames.FILENAME] == "x"
            assert records[0][ImageFieldnames.TARGET_POSITION_X] == 1
            assert records[0][ImageFieldnames.TARGET_POSITION_Y] == 2

            # ----------------------------------------------------------------
            # Now try an update.
            record = {
                ImageFieldnames.WELL_CENTER_X: 123,
                ImageFieldnames.WELL_CENTER_Y: 456,
            }

            subs = [1]
            result = await dataface.update(
                Tablenames.ROCKMAKER_IMAGES,
                record,
                f"{ImageFieldnames.AUTOID} = ?",
                subs=subs,
                why="test update",
            )

            assert result["count"] == 1
            records = await dataface.query(all_sql)

            assert len(records) == 1
            assert records[0][ImageFieldnames.WELL_CENTER_X] == 123
            assert records[0][ImageFieldnames.WELL_CENTER_Y] == 456
