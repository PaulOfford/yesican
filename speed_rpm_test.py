import platform
import can


class CanInterface:
    bus_vector = None
    def read_messages(self):
        if platform.system() == 'Windows':
            self.bus_vector = can.interface.Bus(
                channel='2ABDDE6D', interface='usb2can', dll='/Windows/System32/usb2can.dll', bitrate=100000
            )
        elif platform.system() == 'Linux':
            self.bus_vector = can.interface.Bus(
                channel='can0', interface='socketcan', bitrate=100000
            )

        with self.bus_vector as bus:

            count = 1
            while (True):
                for msg in bus:
                    if msg.arbitration_id == 436:  # 436 (0x1b4) gives speed
                        # (((Byte[1] - 208) * 256) + Byte[0]) / 16 -> gives mph
                        # therefore
                        # (((Byte[1] - 208) * 256) + Byte[0]) / 10 -> gives kph
                        speed = (((int(msg.data[1]) - 208) * 256) + int(msg.data[0])) / 10
                        print("Speed (kph): ", speed)
                        count += 1

                    elif msg.arbitration_id == 170:  # 170 (0xAA) gives speed
                        # ((Byte[5] * 256) + Byte[4] ) / 4
                        rpm = ((int(msg.data[5]) * 256) + int(msg.data[4])) / 4
                        print("Revs (rpm): ", rpm)
                        count += 1

if __name__ == "__main__":
    canbus = CanInterface()
    canbus.read_messages()
