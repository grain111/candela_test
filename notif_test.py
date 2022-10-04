"""
Notifications
-------------
Example showing how to add notifications to a characteristic and handle the responses.
Updated on 2019-07-03 by hbldh <henrik.blidh@gmail.com>
"""

import sys
import asyncio
import platform

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic


# you can change these to match your device or override them from the command line
CHARACTERISTIC_UUID = "8f65073d-9f57-4aaa-afea-397d19d5bbeb"
ADDRESS = "F8:24:41:C6:43:2D"


def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    """Simple notification handler which prints the data received."""
    print(f"{characteristic}: {data}")


async def main(address, char_uuid):
    async with BleakClient(address) as client:
        print(f"Connected: {client.is_connected}")

        # await client.start_notify(char_uuid, notification_handler)
        task = asyncio.create_task(client.start_notify(char_uuid, notification_handler))
        await asyncio.sleep(2)
        await client.stop_notify(char_uuid)
        print("Finished")


if __name__ == "__main__":
    asyncio.run(
        main(
            sys.argv[1] if len(sys.argv) > 1 else ADDRESS,
            sys.argv[2] if len(sys.argv) > 2 else CHARACTERISTIC_UUID,
        )
    )