import logging
from pathlib import Path

# Soakdb3 database.
from soakdb3_api.databases.constants import Tablenames

# Client for direct access to the soakdb3 database for seeding it.
from soakdb3_api.datafaces.context import Context as Soakdb3DatafaceClientContext
from soakdb3_api.datafaces.datafaces import (
    datafaces_get_default as soakdb3_datafaces_get_default,
)

# The model which describes the crystal wells to be injected into soakdb3.
from soakdb3_api.models.crystal_well_model import (
    CrystalWellModel as Soakdb3CrystalWellModel,
)

# The service process startup/teardown context.
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

        # Make the soakdb3 CLIENT context.
        soakdb3_client_context = Soakdb3DatafaceClientContext(
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
            # Client for direct access to the soakdb3 database for seeding it.
            async with soakdb3_client_context:
                # Start the xchembku server context which includes the direct or network-addressable service.
                async with xchembku_server_context:
                    # Start the matching xchembku client context.
                    async with xchembku_client_context:
                        await self.__run_the_test(constants, output_directory)

    # ----------------------------------------------------------------------------------------

    async def __run_the_test(self, constants, output_directory):
        """ """

        # Reference the soakdb3 dataface object which the context has set up as the default.
        soakdb3_dataface = soakdb3_datafaces_get_default()

        # Reference the xchembku dataface object which the context has set up as the default.
        xchembku_dataface = xchembku_datafaces_get_default()

        models = []

        visit = "cm00001-1"
        visit_directory = Path(output_directory) / "visits" / visit
        visit_directory.mkdir(parents=True)

        # Soakdb3 expects visitid to be a visit directory.
        # This is because of how the soadkb3 VBA in the Excel works.
        visitid = str(visit_directory)

        seeded_crystal_plate = "98aa_2021-09-13_RI1000-0276-3drop"
        injected_crystal_plate = "98ab_2021-09-14_RI1000-0276-3drop"

        # ----------------------------------------------------------------
        # Seed the necessary fields in the head table.

        protein = "P1"
        drop_volume = 3.1

        head_record = {
            "Protein": protein,
            "DropVolume": drop_volume,
        }

        # Insert these fields as the (single) row in the soakdb3 database's head table.
        await soakdb3_dataface.insert(  # type: ignore
            visitid,
            Tablenames.HEAD,
            [head_record],
        )

        # ----------------------------------------------------------------
        seed_fields = []
        # Seed row ID 1 with no exising crystal well on it.
        # This row will absorb the first injected well.
        seed_fields.append(
            {
                "id": str(-1),
                "field": "ProteinName",
                "value": "something",
            }
        )
        # Seed row ID 2 with an exising crystal well on it.
        # This row will not be touched by injected wells.
        seed_fields.append(
            {
                "id": str(-2),
                "field": "CrystalPlate",
                "value": seeded_crystal_plate,
            }
        )

        # Send these seeds to the soakdb3 database's body table.
        await soakdb3_dataface.update_body_fields(  # type: ignore
            visitid,
            seed_fields,
        )

        # ----------------------------------------------------------------

        # Make some wells to insert.
        models.append(
            Soakdb3CrystalWellModel(
                LabVisit=visit,
                CrystalPlate=injected_crystal_plate,
                CrystalWell="01A1",
                EchoX=100,
                EchoY=200,
            )
        )

        # Same well again, should be ignored.
        models.append(
            Soakdb3CrystalWellModel(
                LabVisit=visit,
                CrystalPlate=injected_crystal_plate,
                CrystalWell="01A1",
                EchoX=101,
                EchoY=201,
            )
        )

        # Different well.
        models.append(
            Soakdb3CrystalWellModel(
                LabVisit=visit,
                CrystalPlate=injected_crystal_plate,
                CrystalWell="01A2",
                EchoX=200,
                EchoY=300,
            )
        )

        # Write crystal well records.
        await xchembku_dataface.inject_soakdb3_crystal_wells(visitid, models)

        # Check the results
        queried_models = await xchembku_dataface.fetch_soakdb3_crystal_wells(visitid)
        assert len(queried_models) == 3

        # Make sure the original location is not overwritten.
        assert queried_models[0].EchoX == 100

        # A new different well.
        models.append(
            Soakdb3CrystalWellModel(
                LabVisit=visit,
                CrystalPlate=injected_crystal_plate,
                CrystalWell="01A3",
                EchoX=300,
                EchoY=400,
            )
        )

        # Write the full list of crystal well records again
        models[0].EchoX = 103
        await xchembku_dataface.inject_soakdb3_crystal_wells(visitid, models)

        # Check the results, there should be no change to the first ones.
        queried_models = await xchembku_dataface.fetch_soakdb3_crystal_wells(visitid)
        assert len(queried_models) == 4
        assert queried_models[0].ID == "1"
        assert queried_models[0].CrystalWell == "01A1"
        assert queried_models[0].CrystalPlate == injected_crystal_plate
        assert queried_models[0].ProteinName == protein
        assert queried_models[0].DropVolume == drop_volume

        # Row ID 2 was seeded and this don't get the injected crystal well.
        assert queried_models[1].ID == "2"
        assert queried_models[1].CrystalPlate == seeded_crystal_plate
        assert queried_models[1].ProteinName is None
        assert queried_models[1].DropVolume is None

        # The last two should have been injected.
        assert queried_models[2].ID == "3"
        assert queried_models[2].CrystalWell == "01A2"
        assert queried_models[2].CrystalPlate == injected_crystal_plate
        assert queried_models[2].ProteinName == protein
        assert queried_models[2].DropVolume == drop_volume

        assert queried_models[3].ID == "4"
        assert queried_models[3].CrystalWell == "01A3"
        assert queried_models[3].CrystalPlate == injected_crystal_plate
        assert queried_models[3].ProteinName == protein
        assert queried_models[3].DropVolume == drop_volume

        # Make sure the original location is not overwritten.
        assert queried_models[0].EchoX == 100
