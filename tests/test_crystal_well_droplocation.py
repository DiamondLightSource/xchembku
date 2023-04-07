import logging
from typing import Optional

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
from xchembku_api.models.crystal_well_droplocation_model import (
    CrystalWellDroplocationModel,
)
from xchembku_api.models.crystal_well_filter_model import CrystalWellFilterModel
from xchembku_api.models.crystal_well_model import CrystalWellModel

# Server context creator.
from xchembku_lib.datafaces.context import Context as XchembkuDatafaceServerContext

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestCrystalWellDroplocationDirect:
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
        CrystalWellDroplocationTester().main(
            constants, configuration_file, output_directory
        )


# ----------------------------------------------------------------------------------------
class TestCrystalWellDroplocationService:
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
        CrystalWellDroplocationTester().main(
            constants, configuration_file, output_directory
        )


# ----------------------------------------------------------------------------------------
class CrystalWellDroplocationTester(Base):
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
        self.__crystal_plate_model = CrystalPlateModel(
            formulatrix__plate__id=1,
            barcode="xyzw",
            visit=self.__visit,
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
            dataface, CrystalWellFilterModel(is_confirmed=True), 3, "confirmed only"
        )
        await self.__check(
            dataface, CrystalWellFilterModel(is_confirmed=False), 2, "unconfirmed only"
        )

        # Check the anchor query forward.
        await self.__check(
            dataface,
            CrystalWellFilterModel(anchor=models[3].uuid, direction=1, limit=1),
            1,
            "anchored forward",
            filename="004b.jpg",
        )

        # Check the anchor query forward at the end of the list.
        await self.__check(
            dataface,
            CrystalWellFilterModel(anchor=models[5].uuid, direction=1),
            0,
            "anchored forward at the end of the list",
        )

        # Check the anchor query backward.
        await self.__check(
            dataface,
            CrystalWellFilterModel(anchor=models[2].uuid, direction=-1),
            1,
            "anchored backward",
            filename="001a.jpg",
        )

        # Check the anchor query backward at the start of the list.
        await self.__check(
            dataface,
            CrystalWellFilterModel(anchor=models[1].uuid, direction=-1),
            0,
            "anchored at the start of the list",
        )

        # Check the anchor query backward at the start of the list of those unconfirmed.
        await self.__check(
            dataface,
            CrystalWellFilterModel(
                is_confirmed=False, anchor=models[1].uuid, direction=-1
            ),
            0,
            "anchored at the start of the list, backward, unconfirmed",
        )

        # Check the anchor query backward at the start of the list of those unconfirmed.
        await self.__check(
            dataface,
            CrystalWellFilterModel(
                is_confirmed=False, anchor=models[2].uuid, direction=-1
            ),
            0,
            "anchored at the start of the list, forward unconfirmed",
        )

        # Query for list from filename glob.
        crystal_well_models = await self.__check(
            dataface,
            CrystalWellFilterModel(filename_pattern="*a.jpg"),
            3,
            "filename glob",
            filename="001a.jpg",
        )

        assert crystal_well_models[1].filename == "002a.jpg"
        assert crystal_well_models[2].filename == "003a.jpg"

        # --------------------------------------------------------------------------
        # Check the usable queries.
        await self.__check(
            dataface,
            CrystalWellFilterModel(is_confirmed=True, is_usable=False),
            0,
            "confirmed but unusable only",
        )
        crystal_well_models = await self.__check(
            dataface, CrystalWellFilterModel(is_usable=True), 3, "usable only"
        )

        # Change one of the usable to unusable.
        t = CrystalWellDroplocationModel(
            crystal_well_uuid=crystal_well_models[0].uuid,
            confirmed_target_position_x=None,
            confirmed_target_position_y=None,
        )

        await dataface.upsert_crystal_well_droplocations([t])

        # Check the usable queries again.
        await self.__check(
            dataface,
            CrystalWellFilterModel(is_confirmed=True, is_usable=False),
            1,
            "confirmed but unusable only",
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

        letter = "a"
        if self.__injected_count > 3:
            letter = "b"

        filename = "%03d%s.jpg" % (self.__injected_count, letter)
        self.__injected_count += 1

        # Create the well object.
        m = CrystalWellModel(
            crystal_plate_uuid=self.__crystal_plate_model.uuid,
            filename=filename,
        )

        # Write well record.
        await dataface.originate_crystal_wells([m])

        if autolocation:
            # Add a crystal well autolocation.
            ta = CrystalWellAutolocationModel(
                crystal_well_uuid=m.uuid,
                number_of_crystals=10,
            )

            await dataface.originate_crystal_well_autolocations([ta])

        if droplocation:
            # Add a crystal well droplocation.
            td = CrystalWellDroplocationModel(
                crystal_well_uuid=m.uuid,
                confirmed_target_position_x=10,
                confirmed_target_position_y=11,
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

        crystal_well_models = await dataface.fetch_crystal_wells_needing_droplocation(
            filter
        )

        assert len(crystal_well_models) == expected, note

        # All wells should belong to the visit.
        for crystal_well_model in crystal_well_models:
            assert crystal_well_model.visit == self.__visit, f"{note} visit"

        if filename is not None:
            assert crystal_well_models[0].filename == filename, f"{note} filename"

        return crystal_well_models
