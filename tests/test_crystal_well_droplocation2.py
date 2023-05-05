import logging
from typing import List

import pytest

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
from xchembku_api.models.crystal_plate_model import CrystalPlateModel
from xchembku_api.models.crystal_well_autolocation_model import (
    CrystalWellAutolocationModel,
)
from xchembku_api.models.crystal_well_droplocation_model import (
    CrystalWellDroplocationModel,
)
from xchembku_api.models.crystal_well_filter_model import (
    CrystalWellFilterModel,
    CrystalWellFilterSortbyEnum,
)
from xchembku_api.models.crystal_well_model import CrystalWellModel
from xchembku_lib.crystal_plate_objects.crystal_plate_objects import CrystalPlateObjects

# Server context creator.
from xchembku_lib.datafaces.context import Context as XchembkuDatafaceServerContext

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestCrystalWellDroplocation2Direct:
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
        CrystalWellDroplocation2Tester().main(
            constants, configuration_file, output_directory
        )


# ----------------------------------------------------------------------------------------
class TestCrystalWellDroplocation2Service:
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
        CrystalWellDroplocation2Tester().main(
            constants, configuration_file, output_directory
        )


# ----------------------------------------------------------------------------------------
class CrystalWellDroplocation2Tester(Base):
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

        # Make a plate for the wells we will create.
        self.__visit = "cm00001-1"
        self.__barcode = "xyzw"
        self.__crystal_plate_model = CrystalPlateModel(
            formulatrix__plate__id=1,
            barcode=self.__barcode,
            visit=self.__visit,
            thing_type=CrystalPlateThingTypes.SWISS3,
        )

        self.__crystal_plate_object = CrystalPlateObjects().build_object(
            {"type": CrystalPlateThingTypes.SWISS3}
        )

        # Write plate record.
        await dataface.upsert_crystal_plates(
            [self.__crystal_plate_model],
        )

        models = []

        # Inject some wells, all of which will belong to the plate we just made.
        models.append(await self.__inject(dataface, 1))  # 1
        models.append(await self.__inject(dataface, 2))  # 2
        models.append(await self.__inject(dataface, 3))  # 3
        models.append(await self.__inject(dataface, 3))  # 4
        models.append(await self.__inject(dataface, 2))  # 5
        models.append(await self.__inject(dataface, 1))  # 6

        # Check the filtered queries.
        await self.__check(
            dataface,
            CrystalWellFilterModel(
                sortby=CrystalWellFilterSortbyEnum.NUMBER_OF_CRYSTALS,
                direction=1,
            ),
            [3, 4, 2, 5, 1, 6],
            "all, forward",
        )

        await self.__check(
            dataface,
            CrystalWellFilterModel(
                sortby=CrystalWellFilterSortbyEnum.NUMBER_OF_CRYSTALS,
                direction=-1,
            ),
            [6, 1, 5, 2, 4, 3],
            "all, reverse",
        )

        await self.__check(
            dataface,
            CrystalWellFilterModel(
                anchor=models[1].uuid,
                sortby=CrystalWellFilterSortbyEnum.NUMBER_OF_CRYSTALS,
            ),
            [2],
            "anchored, single",
        )

        with pytest.raises(RuntimeError):
            # Does not work without a visit.
            await self.__check(
                dataface,
                CrystalWellFilterModel(
                    anchor=models[1].uuid,
                    sortby=CrystalWellFilterSortbyEnum.NUMBER_OF_CRYSTALS,
                    direction=-1,
                    limit=1,
                ),
                [],
                "anchored, no visit",
            )

        await self.__check(
            dataface,
            CrystalWellFilterModel(
                # Anchor at #2.
                anchor=models[1].uuid,
                visit=self.__visit,
                sortby=CrystalWellFilterSortbyEnum.NUMBER_OF_CRYSTALS,
                direction=1,
                limit=1,
            ),
            [5],
            "anchored, forward",
        )

        await self.__check(
            dataface,
            CrystalWellFilterModel(
                # Anchor at #2.
                anchor=models[1].uuid,
                visit=self.__visit,
                sortby=CrystalWellFilterSortbyEnum.NUMBER_OF_CRYSTALS,
                direction=-1,
                limit=1,
            ),
            [4],
            "anchored, reverse, single",
        )

        await self.__check(
            dataface,
            CrystalWellFilterModel(
                # Anchor at #2.
                anchor=models[1].uuid,
                visit=self.__visit,
                sortby=CrystalWellFilterSortbyEnum.NUMBER_OF_CRYSTALS,
                direction=-1,
                limit=10,
            ),
            [4, 3],
            "anchored, reverse, all",
        )

    # ----------------------------------------------------------------------------------------

    async def __check(
        self,
        dataface,
        filter: CrystalWellFilterModel,
        expected: List[int],
        note: str,
    ):
        """ """

        # Get the full crystal well with auto and confirmed drop locations.
        crystal_well_models = await dataface.fetch_crystal_wells_needing_droplocation(
            filter
        )

        for index, crystal_well_model in enumerate(crystal_well_models):
            logger.debug(
                f"{index+1}. position {crystal_well_model.position} has {crystal_well_model.number_of_crystals} crystals at uuid {crystal_well_model.uuid}"
            )

        expected_positions = []
        got_positions = []
        for index, crystal_well_model in enumerate(crystal_well_models):
            expected_positions.append("A%02da" % (expected[index]))
            got_positions.append(crystal_well_model.position)

        assert expected_positions == got_positions, note

    # ----------------------------------------------------------------------------------------

    async def __inject(self, dataface, number_of_crystals: int):
        """ """

        self.__injected_count += 1
        filename = "%02dA_1.jpg" % (self.__injected_count)
        position = "A%02da" % (self.__injected_count)

        # Create the well object.
        m = CrystalWellModel(
            position=position,
            crystal_plate_uuid=self.__crystal_plate_model.uuid,
            crystal_plate_thing_type=self.__crystal_plate_model.thing_type,
            filename=filename,
        )

        # Write well record.
        await dataface.upsert_crystal_wells([m])

        # Add a crystal well autolocation.
        ta = CrystalWellAutolocationModel(
            crystal_well_uuid=m.uuid,
            number_of_crystals=number_of_crystals,
            well_centroid_x=100,
            well_centroid_y=100,
        )
        await dataface.originate_crystal_well_autolocations([ta])

        # Add a crystal well droplocation.
        td = CrystalWellDroplocationModel(
            crystal_well_uuid=m.uuid,
            confirmed_target_x=150,
            confirmed_target_y=50,
            is_usable=True,
        )

        await dataface.upsert_crystal_well_droplocations([td])

        return m
