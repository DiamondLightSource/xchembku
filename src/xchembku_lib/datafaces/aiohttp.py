import asyncio
import logging
import multiprocessing
import threading

# Utilities.
from dls_utilpack.callsign import callsign
from dls_utilpack.explain import explain
from dls_utilpack.require import require

# Basic things.
from dls_utilpack.thing import Thing

# Dataface protocolj things.
from xchembku_api.datafaces.constants import Commands, Keywords

# Base class for an aiohttp server.
from xchembku_lib.base_aiohttp import BaseAiohttp

# Types of xchembku_dataface.
# Global xchembku_dataface.
from xchembku_lib.datafaces.datafaces import Datafaces

logger = logging.getLogger(__name__)

thing_type = "xchembku_lib.xchembku_datafaces.aiohttp"


# ------------------------------------------------------------------------------------------
class Aiohttp(Thing, BaseAiohttp):
    """
    Object implementing remote procedure calls for xchembku_dataface methods.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None):
        Thing.__init__(self, thing_type, specification)
        BaseAiohttp.__init__(
            self,
            specification["type_specific_tbd"]["aiohttp_specification"],
        )

        self.__actual_dataface = None

    # ----------------------------------------------------------------------------------------
    def callsign(self):
        """"""
        return "%s %s" % ("Dataface.Aiohttp", BaseAiohttp.callsign(self))

    # ----------------------------------------------------------------------------------------
    def activate_process(self):
        """"""

        try:
            multiprocessing.current_process().name = "dataface"

            self.activate_process_base()

        except Exception as exception:
            logger.exception(
                f"unable to start {callsign(self)} process", exc_info=exception
            )

    # ----------------------------------------------------------------------------------------
    def activate_thread(self, loop):
        """
        Called from inside a newly created thread.
        """

        try:
            threading.current_thread().name = "xchembku_dataface"

            self.activate_thread_base(loop)

        except Exception as exception:
            logger.exception(
                f"unable to start {callsign(self)} thread", exc_info=exception
            )

    # ----------------------------------------------------------------------------------------
    async def activate_coro(self):
        """"""
        try:
            # No special routes, we will use protocolj dispathcing only
            route_tuples = []

            # Build a local xchembku_dataface for our back-end.
            self.__actual_dataface = Datafaces().build_object(
                self.specification()["type_specific_tbd"][
                    "actual_xchembku_dataface_specification"
                ]
            )

            # Use a lock around all transaction-based requests.
            # TODO: Remove aiohttp transaction lock and instead use connection pool.
            self.__request_lock = asyncio.Lock()

            # Get the local implementation started.
            await self.__actual_dataface.start()

            await self.activate_coro_base(route_tuples)

        except Exception:
            raise RuntimeError(f"unable to start {callsign(self)} server coro")

    # ----------------------------------------------------------------------------------------
    async def direct_shutdown(self):
        """"""
        try:
            # Disconnect our local dataface connection, i.e. the one which holds the database connection.
            await self.__actual_dataface.disconnect()

        except Exception as exception:
            logger.warning(
                callsign(
                    self, explain(exception, "disconnecting actual xchembku_dataface")
                )
            )

        # Let the base class stop the server listener.
        await self.base_direct_shutdown()

    # ----------------------------------------------------------------------------------------
    async def __do_actually(self, function, args, kwargs):
        """"""

        # logger.info(describe("function", function))
        # logger.info(describe("args", args))
        # logger.info(describe("kwargs", kwargs))

        # Get the function which the caller wants executed.
        function = getattr(self.__actual_dataface, function)

        # Lock out all other requests from running at the same time.
        async with self.__request_lock:

            # Caller wants the function wrapped in a transaction?
            if "as_transaction" in kwargs:
                as_transaction = kwargs["as_transaction"]
                # Take the keyword out of the kwargs because the functions don't have it.
                kwargs.pop("as_transaction")
            else:
                as_transaction = False

            if as_transaction:
                # Make sure we have an actual connection.
                await self.__actual_dataface.establish_database_connection()

                try:
                    await self.__actual_dataface.begin()
                    response = await function(*args, **kwargs)
                    await self.__actual_dataface.commit()
                except Exception:
                    await self.__actual_dataface.rollback()
                    raise
            else:
                response = await function(*args, **kwargs)

        return response

    # ----------------------------------------------------------------------------------------
    async def dispatch(self, request_dict, opaque):
        """"""

        # logger.debug(describe(f"{callsign(self)} request", request_dict))

        command = require("request json", request_dict, Keywords.COMMAND)

        if command == Commands.EXECUTE:
            payload = require("request json", request_dict, Keywords.PAYLOAD)
            response = await self.__do_actually(
                payload["function"], payload["args"], payload["kwargs"]
            )
        else:
            raise RuntimeError("invalid command %s" % (command))

        return response
