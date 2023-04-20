import logging
from pathlib import Path

# The model which describes the crystal wells to be injected into soakdb3.
from soakdb3_api.models.crystal_well_model import (
    CrystalWellModel as Soakdb3CrystalWellModel,
)
from soakdb3_lib.datafaces.context import Context as Soakdb3DatafaceServerContext

# Base class for the tester.
from tests.base import Base

# Client context creator.
from xchembku_api.datafaces.context import Context as XchembkuDatafaceClientContext

# Object managing datafaces.
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default

# Server context creator.
from xchembku_lib.datafaces.context import Context as XchembkuDatafaceServerContext

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestSoakdb3CrystalWellDirect:
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
        Soakdb3CrystalWellTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class TestSoakdb3CrystalWellService:
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
        Soakdb3CrystalWellTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class Soakdb3CrystalWellTester(Base):
    """
    Class to test the dataface droplocation-related endpoints.
    """

    async def _main_coroutine(self, constants, output_directory):
        """ """
        self.__injected_count = 0

        # Get the multiconf from the testing configuration yaml.
        multiconf = self.get_multiconf()

        # Load the multiconf into a dict.
        multiconf_dict = await multiconf.load()

        # Reference the dict entry for the soakdb3 dataface.
        soakdb3_dataface_specification = multiconf_dict[
            "soakdb3_dataface_specification"
        ]

        # Make the soakdb3 server context.
        soakdb3_server_context = Soakdb3DatafaceServerContext(
            soakdb3_dataface_specification
        )

        # Reference the dict entry for the xchembku dataface.
        xchembku_dataface_specification = multiconf_dict[
            "xchembku_dataface_specification"
        ]

        # Make the xchembku server context.
        xchembku_server_context = XchembkuDatafaceServerContext(
            xchembku_dataface_specification
        )

        # Make the xchembku client context.
        xchembku_client_context = XchembkuDatafaceClientContext(
            xchembku_dataface_specification
        )

        # Start the soakdb3 server context which includes the direct or network-addressable service.
        async with soakdb3_server_context:
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

        models = []

        visit = "cm00001-1"
        visit_directory = Path(output_directory) / "visits" / visit
        visit_directory.mkdir(parents=True)

        # Soakdb3 expects visitid to be a visit directory.
        # This is because of how the soadkb3 VBA in the Excel works.
        visitid = str(visit_directory)

        # Make some wells to insert.
        models.append(
            Soakdb3CrystalWellModel(
                LabVisit=visit,
                CrystalPlate="98ab_2021-09-14_RI1000-0276-3drop",
                CrystalWell="01A1",
                EchoX=100,
                EchoY=200,
            )
        )

        # Same well again, should be ignored.
        models.append(
            Soakdb3CrystalWellModel(
                LabVisit=visit,
                CrystalPlate="98ab_2021-09-14_RI1000-0276-3drop",
                CrystalWell="01A1",
                EchoX=101,
                EchoY=201,
            )
        )

        # Different well.
        models.append(
            Soakdb3CrystalWellModel(
                LabVisit=visit,
                CrystalPlate="98ab_2021-09-14_RI1000-0276-3drop",
                CrystalWell="01A2",
                EchoX=200,
                EchoY=300,
            )
        )

        # Write crystal well records.
        await dataface.append_soakdb3_crystal_wells(visitid, models)

        # Check the results
        queried_models = await dataface.fetch_soakdb3_crystal_wells(visitid)
        assert len(queried_models) == 2

        # Make sure the original location is not overwritten.
        assert queried_models[0].EchoX == 100

        # A new different well.
        models.append(
            Soakdb3CrystalWellModel(
                LabVisit=visit,
                CrystalPlate="98ab_2021-09-14_RI1000-0276-3drop",
                CrystalWell="01A3",
                EchoX=300,
                EchoY=400,
            )
        )

        # Write the full list of crystal well records again
        models[0].EchoX = 103
        await dataface.append_soakdb3_crystal_wells(visitid, models)

        # Check the results, there should be no change to the first ones.
        queried_models = await dataface.fetch_soakdb3_crystal_wells(visitid)
        assert len(queried_models) == 3
        assert queried_models[0].CrystalWell == "01A1"
        assert queried_models[1].CrystalWell == "01A2"
        assert queried_models[2].CrystalWell == "01A3"

        # Make sure the original location is not overwritten.
        assert queried_models[0].EchoX == 100
