import platform
import can
import os

from settings_code import Settings

settings = Settings()

class CanInterface:
    global settings
    bus_vector = None
    def read_messages(self):
        if platform.system() == 'Windows':
            self.bus_vector = can.interface.Bus(
                channel='2ABDDE6D', interface='usb2can', dll='/Windows/System32/usb2can.dll', bitrate=100000
            )
        elif platform.system() == 'Linux':
            if settings.get_can_adapter() == "Waveshare":
                os.system('sudo ip link set can0 down')
                os.system('sudo ip link set can0 up type can bitrate 100000')
                self.bus_vector = can.interface.Bus(channel='can0', bustyp='socketcan_ctypes')
            else:
                self.bus_vector = can.interface.Bus(
                    channel='can0', interface='socketcan', bitrate=100000
                )

        with self.bus_vector as bus:

            count = 1
            while (True):
                for msg in bus:
                    print(count, hex(msg.arbitration_id), msg.data.hex(' ', -4))

                    count += 1

if __name__ == "__main__":
    canbus = CanInterface()
    canbus.read_messages()
