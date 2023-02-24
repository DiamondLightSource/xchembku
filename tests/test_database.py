import asyncio
import logging
import multiprocessing

import pytest

from xchembku_api.databases.constants import CrystalWellFieldnames, Tablenames
from xchembku_lib.databases.databases import Databases

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestDatabase:
    def test(self, constants, logging_setup, output_directory):
        """
        Tests the sqlite implementation of Database.
        """

        database_specification = {
            "type": "xchembku_lib.xchembku_databases.aiosqlite",
            "filename": "%s/xchembku_scheduler.sqlite" % (output_directory),
        }

        # Test direct SQL access to the database.
        DatabaseTesterImage().main(
            constants,
            database_specification,
            output_directory,
        )


# ----------------------------------------------------------------------------------------
class _BaseTester:
    """
    Provide asyncio loop and error checking over *Tester classes.
    """

    def main(self, constants, specification, output_directory):
        """
        This is the main program which calls the test using asyncio.
        """

        multiprocessing.current_process().name = "main"

        failure_message = None
        try:
            # Run main test in asyncio event loop.
            asyncio.run(
                self._main_coroutine(constants, specification, output_directory)
            )

        except Exception as exception:
            logger.exception(
                "unexpected exception in the test method", exc_info=exception
            )
            failure_message = str(exception)

        if failure_message is not None:
            pytest.fail(failure_message)


# ----------------------------------------------------------------------------------------
class DatabaseTesterImage(_BaseTester):
    """
    Test direct SQL access to the database.
    """

    async def _main_coroutine(
        self, constants, database_specification, output_directory
    ):
        """ """

        databases = Databases()
        database = databases.build_object(database_specification)

        # Connect to database.
        await database.connect()

        # Write one record.
        await database.insert(
            Tablenames.CRYSTAL_WELLS,
            [
                {
                    CrystalWellFieldnames.FILENAME: "x",
                    CrystalWellFieldnames.TARGET_POSITION_X: "1",
                    CrystalWellFieldnames.TARGET_POSITION_Y: "2",
                }
            ],
        )
        all_sql = f"SELECT * FROM {Tablenames.CRYSTAL_WELLS}"
        records = await database.query(all_sql)
        assert len(records) == 1

        # Bulk insert more records.
        insertable_records = [
            ["f1", 1],
            ["f2", 2],
            ["f3", 3],
            ["f4", 4],
        ]
        await database.execute(
            f"INSERT INTO {Tablenames.CRYSTAL_WELLS}"
            f" ({CrystalWellFieldnames.FILENAME}, {CrystalWellFieldnames.TARGET_POSITION_X})"
            " VALUES (?, ?)",
            insertable_records,
        )

        all_sql = f"SELECT * FROM {Tablenames.CRYSTAL_WELLS}"
        records = await database.query(all_sql)
        assert len(records) == 5

        # Connect from the database... necessary to allow asyncio loop to exit.
        await database.disconnect()
