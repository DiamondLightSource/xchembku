import logging

# Base class for the tester.
from tests.base import Base

# Object managing datafaces.
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default
from xchembku_api.models.crystal_well_autolocation_model import (
    CrystalWellAutolocationModel,
)
from xchembku_api.models.crystal_well_droplocation_model import (
    CrystalWellDroplocationModel,
)
from xchembku_api.models.crystal_well_model import CrystalWellModel

# Context creator.
from xchembku_lib.datafaces.context import Context as XchembkuDatafaceContext

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestCrystalWellDroplocationDirect:
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
        CrystalWellDroplocationTester().main(
            constants, configuration_file, output_directory
        )


# ----------------------------------------------------------------------------------------
class TestCrystalWellDroplocationService:
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
        CrystalWellDroplocationTester().main(
            constants, configuration_file, output_directory
        )


# ----------------------------------------------------------------------------------------
class CrystalWellDroplocationTester(Base):
    """
    Class to test the dataface well-related endpoints.

    This test creates two crystal wells and assigns one of them an autolocation.
    Then it selects crystal wells needing droplocations, which should be just the one.
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
            # Write two well records.
            filename1 = "abc.jpg"
            crystal_well_model1 = CrystalWellModel(filename=filename1)
            filename2 = "xyz.jpg"
            crystal_well_model2 = CrystalWellModel(filename=filename2)
            await dataface.originate_crystal_wells(
                [crystal_well_model1, crystal_well_model2]
            )

            # Fetch all the wells which need droplocation.
            crystal_well_models = (
                await dataface.fetch_crystal_wells_needing_droplocation(limit=100)
            )
            # Initially there are none.
            assert len(crystal_well_models) == 0

            # ---------------------------------------------------------------------
            # Add a crystal well autolocation.
            crystal_well_autolocation_model = CrystalWellAutolocationModel(
                crystal_well_uuid=crystal_well_model1.uuid
            )

            crystal_well_autolocation_model.number_of_crystals = 10
            await dataface.originate_crystal_well_autolocations(
                [crystal_well_autolocation_model]
            )

            # Fetch all the wells which need droplocation.
            crystal_well_models = (
                await dataface.fetch_crystal_wells_needing_droplocation(limit=100)
            )

            # Now there is 1 which needs a droplocation.
            assert len(crystal_well_models) == 1
            assert crystal_well_models[0].filename == filename1

            # ----------------------------------------------------------------
            # Add a crystal well droplocation.
            crystal_well_droplocation_model = CrystalWellDroplocationModel(
                crystal_well_uuid=crystal_well_model1.uuid
            )

            crystal_well_droplocation_model.confirmed_target_position_x = 10
            crystal_well_droplocation_model.confirmed_target_position_y = 11
            await dataface.originate_crystal_well_droplocations(
                [crystal_well_autolocation_model]
            )

            # Fetch all the wells which need droplocation.
            crystal_well_models = (
                await dataface.fetch_crystal_wells_needing_droplocation(limit=100)
            )

            # Now there are none needing droplocation.
            assert len(crystal_well_models) == 0

            # Fetch all the wells which need autolocation.
            crystal_well_models = (
                await dataface.fetch_crystal_wells_needing_autolocation(limit=100)
            )

            # There is still one needing autolocation.
            assert len(crystal_well_models) == 1
