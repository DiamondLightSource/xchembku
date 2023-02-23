# This tutorial program shows you how to update an image record.

import asyncio
import json

from xchembku_api.databases.constants import CrystalWellFieldnames
from xchembku_api.datafaces.constants import Types
from xchembku_api.datafaces.context import Context

# Specify the client type and remote endpoint.
client_specification = {
    "type": Types.AIOHTTP,
    "type_specific_tbd": {
        "aiohttp_specification": {"client": "http://localhost:27821"}
    },
}


async def tutorial():
    async with Context(client_specification) as client_interface:
        # This is the request which is sent to update the image.
        request = {
            "filename": ".*1.jpg",
            CrystalWellFieldnames.CRYSTAL_PROBABILITY: 0.9,
        }

        # Send the request to the server and get the response.
        response = await client_interface.update_crystal_well(request)

        # Show the response, which is None if success, otherwise a dict with errors in it.
        print(json.dumps(response, indent=4))


if __name__ == "__main__":
    asyncio.run(tutorial())
