import asyncio
from bleak import BleakClient, BleakScanner
import logging
import struct
from bleak_retry_connector import establish_connection
from bleak.backends.device import BLEDevice

NOTIFY_UUID = "8f65073d-9f57-4aaa-afea-397d19d5bbeb"
CONTROL_UUID = "aa7d3f34-2d4f-41e0-807f-52fbf8cf7443"

COMMAND_STX = 0x43
CMD_PAIR = 0x67
CMD_PAIR_ON = 0x02
RES_PAIR = 0x63
CMD_POWER = 0x40
CMD_POWER_ON = 0x01
CMD_POWER_OFF = 0x02
CMD_COLOR = 0x41
CMD_BRIGHTNESS = 0x42
CMD_TEMP = 0x43
CMD_RGB = 0x41
CMD_GETSTATE = 0x44
CMD_GETSTATE_SEC = 0x02
RES_GETSTATE = 0x45
CMD_GETNAME = 0x52
RES_GETNAME = 0x53
CMD_GETVER = 0x5C
RES_GETVER = 0x5D
CMD_GETSERIAL = 0x5E
RES_GETSERIAL = 0x5F
RES_GETTIME = 0x62

LOGGER = logging.getLogger(__name__)

class CandelaInstance:
    def __init__(self, ble_device: BLEDevice) -> None:
        self._mac = ble_device.address
        self._device = BleakClient(ble_device)
        self._ble_device = ble_device
        self._is_on = None
        self._connected = None
        self._brightness = None
        self._device.set_disconnected_callback(self.disconnected_callback)

    def disconnected_callback(self, device):
        self.disconnect()

    async def _send(self, data):
      
        if (not self._connected):
            await self.connect()
        print(CONTROL_UUID, data)
        await self._device.write_gatt_char(CONTROL_UUID, data)
        return True

    def notification_handler(self, sender, data):
        """Simple notification handler which prints the data received."""
        state = struct.unpack(">xxBBBBBBBhx6x", data)
        # print(state)
        print("{0}: {1}".format(sender, data.hex(" ")))
    
    async def notify(self):
        await self._device.start_notify(NOTIFY_UUID, self.notification_handler)
        await asyncio.sleep(1.0)
        await self._device.stop_notify(NOTIFY_UUID)

    @property
    def mac(self):
        return self._mac

    @property
    def is_on(self):
        return self._is_on

    @property
    def brightness(self):
        return self._brightness

    async def set_brightness(self, intensity: int):
        bits = struct.pack("BBB15x", COMMAND_STX, CMD_BRIGHTNESS, intensity)
        await self._send(bits)

        self._brightness = intensity

    async def turn_on(self):
        bits = struct.pack("BBB15x", COMMAND_STX, CMD_POWER, CMD_POWER_ON)
        print(bits)

        await self._send(bits)
        self._is_on = True

    async def turn_off(self):
        bits = struct.pack("BBB15x", COMMAND_STX, CMD_POWER, CMD_POWER_OFF)

        await self._send(bits)
        self._is_on = False
    
    async def pair(self):
        bits = struct.pack("BBB15x", COMMAND_STX, CMD_PAIR, CMD_PAIR_ON)
        await self._send(bits)

        # await self._send(bytes.fromhex("43 67 c8 97 57 62 f0 24 00 00 00 00 00 00 00 00 00 00"))

        # await self._send(bytes.fromhex("43 5c 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
        # await self._send(bytes.fromhex("43 44 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
        # await self._send(bytes.fromhex("43 52 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
        # await self._send(bytes.fromhex("43 4c 03 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
        # await self._send(bytes.fromhex("43 80 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
        # await self._send(bytes.fromhex("43 4c 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
        # await self._send(bytes.fromhex("43 80 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
        # await self._send(bytes.fromhex("43 a3 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
        # await self._send(bytes.fromhex("43 a2 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"))
        # await self._device.pair()
        print("paired!")
        await asyncio.sleep(5)

    async def connect(self):
        self._device = await establish_connection(
            BleakClient, 
            device=self._ble_device, 
            name=self._mac, 
            disconnected_callback=self.disconnected_callback,
            max_attempts=3,
        )
        # await self._device.connect()
        print("connected!")
        
        await asyncio.sleep(1)
        self._connected = True
        await self.pair()
        # await self._device.pair()
        # print("start notify")
        # await self._device.start_notify(NOTIFY_UUID, self.notification_handler)


    async def disconnect(self):

        await self._device.disconnect()
        self._connected = False





if __name__ == "__main__":

    async def test_light() -> None:
        device = await BleakScanner.find_device_by_address("F8:24:41:C6:43:2D")
        print(device)
        lamp = CandelaInstance(device)
        # lamp = CandelaInstance("F8:24:41:C6:43:2D")
        print("created instance")
        await lamp.connect()

        await lamp.turn_on()
        await asyncio.sleep(2)
        await lamp.set_brightness(100)
        await asyncio.sleep(2)
        await lamp.set_brightness(90)
        await asyncio.sleep(2)
        await lamp.set_brightness(70)
        await asyncio.sleep(2)
        await lamp.set_brightness(10)
        await asyncio.sleep(2)
        await lamp.turn_off()
        await lamp.turn_on()
        await asyncio.sleep(2)
        for i in range(1000):
            print(i)
            await lamp.turn_on()
            await asyncio.sleep(0.5)
            await lamp.turn_off()
            await asyncio.sleep(0.5)
        await asyncio.sleep(2)
        await lamp.turn_off()

        await asyncio.sleep(200)
        await lamp.turn_on()
        await lamp.disconnect()
        await asyncio.sleep(2)

    asyncio.run(asyncio.run(test_light()))