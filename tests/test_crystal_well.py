import logging

# Base class for the tester.
from tests.base import Base

# Object managing datafaces.
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default
from xchembku_api.models.crystal_well_autolocation_model import (
    CrystalWellAutolocationModel,
)
from xchembku_api.models.crystal_well_model import CrystalWellModel

# Context creator.
from xchembku_lib.datafaces.context import Context as XchembkuDatafaceContext

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestCrystalWellDirect:
    """
    Test dataface interface by direct call.
    """

    def test_dataface_multiconf(
        self,
        constants,
        logging_setup,
        output_directory,
    ):
        configuration_file = "tests/configurations/direct.yaml"
        CrystalWellTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class TestCrystalWellService:
    """
    Test dataface interface through network interface.
    """

    def test_dataface_multiconf(
        self,
        constants,
        logging_setup,
        output_directory,
    ):
        """ """

        configuration_file = "tests/configurations/service.yaml"
        CrystalWellTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class CrystalWellTester(Base):
    """
    Class to test the dataface well-related endpoints.
    """

    async def _main_coroutine(self, constants, output_directory):
        """ """

        # Get the multiconf from the testing configuration yaml.
        multiconf = self.get_multiconf()

        # Load the multiconf into a dict.
        multiconf_dict = await multiconf.load()

        # Reference the dict entry for the xchembku dataface.
        xchembku_context = XchembkuDatafaceContext(
            multiconf_dict["xchembku_dataface_specification"]
        )

        # Start the xchembku context which includes the direct or network-addressable service.
        async with xchembku_context:

            # Reference the dataface object which the context has set up as the default.
            dataface = xchembku_datafaces_get_default()

            # Write one well record.
            filename = "abc.jpg"
            well_model = CrystalWellModel(filename=filename)
            await dataface.originate_crystal_wells([well_model])

            # Fetch all the models which need autolocation.
            crystal_well_models = (
                await dataface.fetch_crystal_wells_needing_autolocation()
            )

            assert len(crystal_well_models) == 1

            assert crystal_well_models[0].filename == filename
            return

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

            records = await dataface.fetch_crystal_wells_needing_autolocation()
            assert len(records) == 1
            assert records[0][CrystalWellFieldnames.WELL_CENTER_X] == 123
            assert records[0][CrystalWellFieldnames.WELL_CENTER_Y] == 456
