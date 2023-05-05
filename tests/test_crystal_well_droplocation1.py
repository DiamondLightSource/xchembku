import logging
from typing import Optional

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
from xchembku_api.models.crystal_well_filter_model import CrystalWellFilterModel
from xchembku_api.models.crystal_well_model import CrystalWellModel
from xchembku_lib.crystal_plate_objects.crystal_plate_objects import CrystalPlateObjects

# Server context creator.
from xchembku_lib.datafaces.context import Context as XchembkuDatafaceServerContext

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestCrystalWellDroplocation1Direct:
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
        CrystalWellDroplocation1Tester().main(
            constants, configuration_file, output_directory
        )


# ----------------------------------------------------------------------------------------
class TestCrystalWellDroplocation1Service:
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
        CrystalWellDroplocation1Tester().main(
            constants, configuration_file, output_directory
        )


# ----------------------------------------------------------------------------------------
class CrystalWellDroplocation1Tester(Base):
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
        models.append(await self.__inject(dataface, False, False))
        models.append(await self.__inject(dataface, True, True))
        models.append(await self.__inject(dataface, True, False))
        models.append(await self.__inject(dataface, True, True))
        models.append(await self.__inject(dataface, True, True))
        models.append(await self.__inject(dataface, True, False))

        # --------------------------------------------------------------------------
        # Query for list from filename glob.
        crystal_well_models = await self.__check(
            dataface,
            CrystalWellFilterModel(filename_pattern="*A_1.jpg"),
            3,
            "filename glob",
            filename="02A_1.jpg",
        )

        assert (
            crystal_well_models[1].filename == "03A_1.jpg"
        ), "filename glob, second response"
        assert (
            crystal_well_models[2].filename == "04A_1.jpg"
        ), "filename glob, third response"

        # --------------------------------------------------------------------------

        # Check the filtered queries.
        await self.__check(dataface, CrystalWellFilterModel(), 5, "no limit, all")

        # Upsert all with the same values to make sure it doesn't make new records.
        records = await dataface.query(
            "SELECT * FROM crystal_well_droplocations",
            why="[UPSCHK] direct query all drop locations",
        )
        m = [CrystalWellDroplocationModel(**record) for record in records]
        await dataface.upsert_crystal_well_droplocations(m, why="[UPSCHK]")
        await self.__check(
            dataface, CrystalWellFilterModel(), 5, "no limit, all after upsert"
        )

        await self.__check(dataface, CrystalWellFilterModel(limit=1), 1, "limit 1")
        await self.__check(dataface, CrystalWellFilterModel(limit=2), 2, "limit 2")
        await self.__check(
            dataface, CrystalWellFilterModel(is_decided=True), 3, "confirmed only"
        )
        await self.__check(
            dataface,
            CrystalWellFilterModel(barcode=self.__barcode, is_decided=True),
            3,
            "confirmed only, barcode",
        )
        await self.__check(
            dataface,
            CrystalWellFilterModel(barcode="abcd", is_decided=True),
            0,
            "confirmed only, other barcode",
        )
        await self.__check(
            dataface, CrystalWellFilterModel(is_decided=False), 2, "unconfirmed only"
        )

        # Check the anchor query forward.
        await self.__check(
            dataface,
            CrystalWellFilterModel(
                visit=self.__visit,
                anchor=models[3].uuid,
                direction=1,
                limit=1,
            ),
            1,
            "anchored forward",
            filename="05B_1.jpg",
        )

        # Check the anchor query forward at the end of the list.
        await self.__check(
            dataface,
            CrystalWellFilterModel(
                visit=self.__visit,
                anchor=models[5].uuid,
                direction=1,
            ),
            0,
            "anchored forward at the end of the list",
        )

        # Check the anchor query backward.
        await self.__check(
            dataface,
            CrystalWellFilterModel(
                visit=self.__visit,
                anchor=models[2].uuid,
                direction=-1,
                limit=1,
            ),
            1,
            "anchored backward",
            filename="02A_1.jpg",
        )

        # Check the anchor query backward at the start of the list.
        await self.__check(
            dataface,
            CrystalWellFilterModel(
                visit=self.__visit,
                anchor=models[1].uuid,
                direction=-1,
            ),
            0,
            "anchored at the start of the list",
        )

        # Check the anchor query backward at the start of the list of those unconfirmed.
        await self.__check(
            dataface,
            CrystalWellFilterModel(
                is_decided=False,
                visit=self.__visit,
                anchor=models[1].uuid,
                direction=-1,
            ),
            0,
            "anchored at the start of the list, backward, unconfirmed",
        )

        # Check the anchor query backward at the start of the list of those unconfirmed.
        await self.__check(
            dataface,
            CrystalWellFilterModel(
                is_decided=False,
                visit=self.__visit,
                anchor=models[2].uuid,
                direction=-1,
            ),
            0,
            "anchored at the start of the list, forward unconfirmed",
        )

        # --------------------------------------------------------------------------
        # Check the usable queries.
        await self.__check(
            dataface,
            CrystalWellFilterModel(is_decided=True, is_usable=False),
            0,
            "confirmed but unusable only (1)",
        )
        crystal_well_models = await self.__check(
            dataface,
            CrystalWellFilterModel(
                visit=self.__visit,
                is_usable=True,
            ),
            3,
            "usable only, visit",
        )

        crystal_well_models = await self.__check(
            dataface,
            CrystalWellFilterModel(
                barcode=self.__barcode,
                is_usable=True,
            ),
            3,
            "usable only, barcode",
        )

        # Change one of the usable to unusable.
        t = CrystalWellDroplocationModel(
            crystal_well_uuid=crystal_well_models[0].uuid,
            is_usable=False,
        )

        await dataface.upsert_crystal_well_droplocations([t])

        # Check the usable queries again.
        await self.__check(
            dataface,
            CrystalWellFilterModel(
                visit=self.__visit,
                is_decided=True,
                is_usable=False,
            ),
            1,
            "confirmed but unusable only (2)",
        )
        crystal_well_models = await self.__check(
            dataface,
            CrystalWellFilterModel(is_usable=True),
            2,
            "usable only after upsert",
        )

    # ----------------------------------------------------------------------------------------

    async def __inject(self, dataface, autolocation: bool, droplocation: bool):
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
            # Add a crystal well autolocation.
            ta = CrystalWellAutolocationModel(
                crystal_well_uuid=m.uuid,
                number_of_crystals=self.__injected_count,
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
                is_usable=True,
            )

            await dataface.upsert_crystal_well_droplocations([td])

        return m

    # ----------------------------------------------------------------------------------------

    async def __check(
        self,
        dataface,
        filter: CrystalWellFilterModel,
        expected: int,
        note: str,
        filename: Optional[str] = None,
    ):
        """ """

        # Get the full crystal well with auto and confirmed drop locations.
        crystal_well_models = await dataface.fetch_crystal_wells_needing_droplocation(
            filter
        )

        # Make sure we got enough.
        assert len(crystal_well_models) == expected, note

        if filename is not None:
            assert crystal_well_models[0].filename == filename, f"{note} filename"

        for crystal_well_model in crystal_well_models:
            # All wells should belong to the visit.
            assert crystal_well_model.visit == self.__visit, f"{note} visit"

            # All present confirmed drop locations should be consistent.
            if (
                crystal_well_model.well_centroid_x is not None
                and crystal_well_model.confirmed_target_x is not None
                and crystal_well_model.well_centroid_y is not None
                and crystal_well_model.confirmed_target_y is not None
            ):

                # Use the template plate to predict the microns.
                (
                    microns_x,
                    microns_y,
                ) = self.__crystal_plate_object.compute_drop_location_microns(
                    crystal_well_model.dict()
                )
                assert crystal_well_model.confirmed_target_x == 150
                assert crystal_well_model.confirmed_microns_x == microns_x
                assert crystal_well_model.confirmed_target_y == 50
                assert crystal_well_model.confirmed_microns_y == microns_y

        return crystal_well_models
