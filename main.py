import platform
import can
import time


class CanInterface:
    def read_messages(self):
        with can.interface.Bus(bustype="usb2can", channel="2ABDDE6D", bitrate=100000,
                               dll='/Windows/System32/usb2can.dll') as bus:

            count = 1
            while (True):
                for msg in bus:
                    print(count, hex(msg.arbitration_id), msg.data.hex(' ', -4))

                    count += 1

if __name__ == "__main__":
    canbus = CanInterface()
    canbus.read_messages()
