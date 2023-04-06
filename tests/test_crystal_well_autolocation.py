import logging

# Base class for the tester.
from tests.base import Base

# Client context creator.
from xchembku_api.datafaces.context import Context as XchembkuDatafaceClientContext

# Object managing datafaces.
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default
from xchembku_api.models.crystal_plate_model import CrystalPlateModel
from xchembku_api.models.crystal_well_autolocation_model import (
    CrystalWellAutolocationModel,
)
from xchembku_api.models.crystal_well_model import CrystalWellModel

# Server context creator.
from xchembku_lib.datafaces.context import Context as XchembkuDatafaceServerContext

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestCrystalWellAutolocationDirectPoll:
    """
    Test dataface interface by direct call.
    """

    def test(
        self,
        constants,
        logging_setup,
        output_directory,
    ):
        configuration_file = "tests/configurations/direct.yaml"
        CrystalWellAutolocationTester().main(
            constants, configuration_file, output_directory
        )


# ----------------------------------------------------------------------------------------
class TestCrystalWellAutolocationService:
    """
    Test dataface interface through network interface.
    """

    def test(
        self,
        constants,
        logging_setup,
        output_directory,
    ):
        """ """

        configuration_file = "tests/configurations/service.yaml"
        CrystalWellAutolocationTester().main(
            constants, configuration_file, output_directory
        )


# ----------------------------------------------------------------------------------------
class CrystalWellAutolocationTester(Base):
    """
    Class to test the dataface autolocation-related endpoints.
    """

    async def _main_coroutine(self, constants, output_directory):
        """ """

        # Get the multiconf from the testing configuration yaml.
        multiconf = self.get_multiconf()

        # Load the multiconf into a dict.
        multiconf_dict = await multiconf.load()

        # Reference the dict entry for the xchembku dataface.
        xchembku_dataface_specification = multiconf_dict[
            "xchembku_dataface_specification"
        ]

        # Make the server context.
        xchembku_server_context = XchembkuDatafaceServerContext(
            xchembku_dataface_specification
        )

        # Make the client context.
        xchembku_client_context = XchembkuDatafaceClientContext(
            xchembku_dataface_specification
        )

        # Start the xchembku server context which includes the direct or network-addressable service.
        async with xchembku_server_context:
            # Start the matching xchembku client context.
            async with xchembku_client_context:
                await self.__run_the_test(constants, output_directory)

    # ----------------------------------------------------------------------------------------

    async def __run_the_test(self, constants, output_directory):
        """ """

        # Reference the dataface object which the context has set up as the default.
        dataface = xchembku_datafaces_get_default()

        # Make a plate for the wells we will create.
        crystal_plate_model = CrystalPlateModel(
            formulatrix__plate__id=1,
            barcode="xyzw",
            visit="cm00001-1",
        )

        # Write two well records.
        filename1 = "abc.jpg"
        crystal_well_model1 = CrystalWellModel(
            crystal_plate_uuid=crystal_plate_model.uuid, filename=filename1
        )
        filename2 = "xyz.jpg"
        crystal_well_model2 = CrystalWellModel(
            crystal_plate_uuid=crystal_plate_model.uuid, filename=filename2
        )
        await dataface.originate_crystal_wells(
            [crystal_well_model1, crystal_well_model2]
        )

        # Fetch all the wells which need autolocation.
        crystal_well_models = await dataface.fetch_crystal_wells_needing_autolocation(
            limit=100
        )

        assert len(crystal_well_models) == 2

        assert crystal_well_models[0].filename == filename1
        assert crystal_well_models[1].filename == filename2

        # ----------------------------------------------------------------
        # Now try adding a crystal well autolocation.
        crystal_well_autolocation_model = CrystalWellAutolocationModel(
            crystal_well_uuid=crystal_well_model1.uuid
        )

        crystal_well_autolocation_model.number_of_crystals = 10
        await dataface.originate_crystal_well_autolocations(
            [crystal_well_autolocation_model]
        )

        # Fetch all the wells which need autolocation, which now there is only one.
        crystal_well_models = await dataface.fetch_crystal_wells_needing_autolocation(
            limit=100
        )

        # Now there is only one needing autolocation.
        assert len(crystal_well_models) == 1
        assert crystal_well_models[0].filename == filename2

        # ----------------------------------------------------------------
        # Now try adding an autolocation to the second well.
        crystal_well_autolocation_model = CrystalWellAutolocationModel(
            crystal_well_uuid=crystal_well_model2.uuid
        )

        crystal_well_autolocation_model.number_of_crystals = 10
        await dataface.originate_crystal_well_autolocations(
            [crystal_well_autolocation_model]
        )

        # Fetch all the wells which need autolocation.
        crystal_well_models = await dataface.fetch_crystal_wells_needing_autolocation(
            limit=100
        )

        # Now there are no more needing autolocation.
        assert len(crystal_well_models) == 0
