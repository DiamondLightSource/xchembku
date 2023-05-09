import logging
from typing import List, Optional

# Base class for the tester.
from tests.base import Base

# Types which the CrystalPlateObjects factory can use to build an instance.
from xchembku_api.crystal_plate_objects.constants import (
    ThingTypes as CrystalPlateThingTypes,
)

# Client context creator.
from xchembku_api.datafaces.context import Context as XchembkuDatafaceClientContext

# Object managing datafaces.
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default
from xchembku_api.models.crystal_plate_filter_model import CrystalPlateFilterModel
from xchembku_api.models.crystal_plate_model import CrystalPlateModel
from xchembku_api.models.crystal_plate_report_model import CrystalPlateReportModel
from xchembku_api.models.crystal_well_autolocation_model import (
    CrystalWellAutolocationModel,
)
from xchembku_api.models.crystal_well_droplocation_model import (
    CrystalWellDroplocationModel,
)
from xchembku_api.models.crystal_well_model import CrystalWellModel

# Server context creator.
from xchembku_lib.datafaces.context import Context as XchembkuDatafaceServerContext

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestCrystalPlateReportDirect:
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
        CrystalPlateReportTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class TestCrystalPlateReportService:
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
        CrystalPlateReportTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class CrystalPlateReportTester(Base):
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

        # Make a plate which will put one well, needing no intervention
        self.__visit = "cm00001-1"
        self.__barcode = "xyzv"
        self.__crystal_plate_model = CrystalPlateModel(
            formulatrix__plate__id=1,
            barcode=self.__barcode,
            visit=self.__visit,
            thing_type=CrystalPlateThingTypes.SWISS3,
        )

        # Write plate record.
        await dataface.upsert_crystal_plates(
            [self.__crystal_plate_model],
        )

        await self.__inject(
            dataface, True, True, True, is_exported_to_soakdb3=True
        )  # Decided usable, exported.

        # Make a plate for the wells we will create.
        self.__visit = "cm00001-1"
        self.__barcode = "xyzw"
        self.__crystal_plate_model = CrystalPlateModel(
            formulatrix__plate__id=2,
            barcode=self.__barcode,
            visit=self.__visit,
            thing_type=CrystalPlateThingTypes.SWISS3,
        )

        # Write plate record.
        await dataface.upsert_crystal_plates(
            [self.__crystal_plate_model],
        )
        # Inject some wells, all of which will belong to the plate we just made.
        await self.__inject(dataface, False, False)  # Not chimped.
        await self.__inject(dataface, False, False)  # Not chimped.

        await self.__inject(dataface, True, False)  # Not viewed, aka undecided.
        await self.__inject(  # No crystals, not viewed, aka undecided.
            dataface, True, False, number_of_crystals=0
        )

        await self.__inject(dataface, True, True)  # Viewed but undecided.
        await self.__inject(  # No crystals, viewed, but undecided.
            dataface, True, True, number_of_crystals=0
        )

        await self.__inject(dataface, True, True, False)  # Decided unusable.
        await self.__inject(dataface, True, True, False)  # Decided usable.
        await self.__inject(dataface, True, True, True)  # Decided usable.
        await self.__inject(dataface, True, True, True)  # Decided usable.
        await self.__inject(
            dataface, True, True, True, is_exported_to_soakdb3=True
        )  # Decided usable, exported.

        # Get the full list.
        crystal_plate_report_models: List[
            CrystalPlateReportModel
        ] = await dataface.report_crystal_plates(CrystalPlateFilterModel(direction=-1))
        assert len(crystal_plate_report_models) == 2

        crystal_plate_report_model: CrystalPlateReportModel = (
            crystal_plate_report_models[0]
        )
        assert crystal_plate_report_model.collected_count == 11
        assert crystal_plate_report_model.chimped_count == 9
        assert crystal_plate_report_model.undecided_count == 4
        assert crystal_plate_report_model.undecided_crystals_count == 2
        assert crystal_plate_report_model.decided_count == 5
        assert crystal_plate_report_model.decided_usable_count == 3
        assert crystal_plate_report_model.decided_unusable_count == 2
        assert crystal_plate_report_model.exported_count == 1
        assert crystal_plate_report_model.usable_unexported_count == 2

        # ----------------------------------------------------------------------
        # Get those which have no undecided crystals and no unexported wells, aka need no intervention.
        crystal_plate_report_models: List[
            CrystalPlateReportModel
        ] = await dataface.report_crystal_plates(
            CrystalPlateFilterModel(needing_intervention=False)
        )

        assert len(crystal_plate_report_models) == 1
        assert crystal_plate_report_models[0].formulatrix__plate__id == 1

        # ----------------------------------------------------------------------
        # Get those which have either undecided crystals or unexported wells, aka need intervention.
        crystal_plate_report_models: List[
            CrystalPlateReportModel
        ] = await dataface.report_crystal_plates(
            CrystalPlateFilterModel(needing_intervention=True)
        )

        assert len(crystal_plate_report_models) == 1
        assert crystal_plate_report_models[0].formulatrix__plate__id == 2

    # ----------------------------------------------------------------------------------------

    async def __inject(
        self,
        dataface,
        autolocation: bool,
        droplocation: bool,
        is_usable: Optional[bool] = None,
        number_of_crystals: Optional[int] = None,
        is_exported_to_soakdb3: Optional[bool] = None,
    ):
        """ """

        letter = "A"
        if self.__injected_count > 3:
            letter = "B"

        self.__injected_count += 1
        filename = "%02d%s_1.jpg" % (self.__injected_count, letter)
        position = "%s%02da" % (letter, self.__injected_count)

        # Create the well object.
        m = CrystalWellModel(
            position=position,
            crystal_plate_uuid=self.__crystal_plate_model.uuid,
            crystal_plate_thing_type=self.__crystal_plate_model.thing_type,
            filename=filename,
        )

        # Write well record.
        await dataface.upsert_crystal_wells([m])

        if autolocation:
            if number_of_crystals is None:
                number_of_crystals = self.__injected_count
            # Add a crystal well autolocation.
            ta = CrystalWellAutolocationModel(
                crystal_well_uuid=m.uuid,
                number_of_crystals=number_of_crystals,
                well_centroid_x=100,
                well_centroid_y=100,
            )

            await dataface.originate_crystal_well_autolocations([ta])

        if droplocation:
            # Add a crystal well droplocation.
            td = CrystalWellDroplocationModel(
                crystal_well_uuid=m.uuid,
                confirmed_target_x=150,
                confirmed_target_y=50,
                is_usable=is_usable,
            )
            if is_exported_to_soakdb3 is not None:
                td.is_exported_to_soakdb3 = is_exported_to_soakdb3

            await dataface.upsert_crystal_well_droplocations([td])

        return m
