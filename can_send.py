import platform
import can
import os
import time
import pandas as pd

from settings_code import Settings
from my_logger import microsec_message

settings = Settings()


class CanInterface:
    global settings
    can1 = None

    def open_interface(self):
        try:
            if platform.system() == 'Windows':
                self.can1 = can.interface.Bus(
                    channel='2ABDDE6D', interface='usb2can', dll='/Windows/System32/usb2can.dll', bitrate=100000
                )
            elif platform.system() == 'Linux':
                if settings.get_can_adapter() == "Waveshare":
                    os.system('sudo ip link set can1 down')
                    os.system('sudo ip link set can1 up type can bitrate 100000')
                    self.can1 = can.interface.Bus(channel='can1', interface='socketcan')
                else:
                    self.can1 = can.interface.Bus(
                        channel='can1', interface='socketcan', bitrate=100000
                    )
        except:
            microsec_message(1, "Attempt to open the CAN interface failed")

    def send_messages(self, msg):
        try:
            self.can1.send(msg)
            microsec_message(5, str(msg))
        except:
            microsec_message(1, "Message send failed")

if __name__ == "__main__":
    canbus = CanInterface()
    canbus.open_interface()

    test_data_frame = pd.read_csv('test_data.csv')
    last_time_offset = 0

    for i, row in test_data_frame.iterrows():
        # calculate the delay needed
        time_offset = float(row['Time (s)'])

        # we need to allow for the case where the starting offset is not zero
        if i == 0:
            last_time_offset = time_offset

        time.sleep(time_offset - last_time_offset)
        last_time_offset = time_offset

        microsec_message(5, "Test message read")

        # msg.arbitration_id == 436 - Speed
        # multiply by 10
        # add 208 * 256
        # and then place in data byte 0 & 1, little endian
        dash_speed = (int(row['SPEED BMW (kph)']) * 10) + (208 * 256)
        byte1 = int(dash_speed/256)
        byte0 = dash_speed - (byte1 * 256)
        msg = can.Message(
            arbitration_id=0x1b4,
            data=[byte0, byte1, 0xe2, 0xf4, 0x16, 0x30, 0xfc, 0xa1],
            is_extended_id=False
        )
        canbus.send_messages(msg)

        # msg.arbitration_id == 170 - RPM
        # multiply by 4
        # and then place in data byte 4 & 5, little endian
        eng_rpm = int(row['RPM']) * 4
        byte5 = int(eng_rpm/256)
        byte4 = eng_rpm - (byte5 * 256)
        msg = can.Message(
            arbitration_id=0x0aa,
            data=[0x67, 0x32, 0xa0, 0x00, byte4, byte5, 0x00, 0x00],
            is_extended_id=False
        )
        canbus.send_messages(msg)

        # msg.arbitration_id == 414 - Brake pressure
        # byte 6
        brake_pressure = int(row['BRAKE PRESS (bar)'])
        byte6 = int(brake_pressure)
        # ToDo: I'm not sure this message has the full brake pressure detail
        # the pressure in the RS3 export has two decimal places
        # we can't accommodate the level of detail in one byte
        # need to find the correct message and calibrate against the Aim Solo
        msg = can.Message(
            arbitration_id=0x19e,
            data=[0x00, 0xec, 0x3f, 0xfc, 0xfe, 0x41, byte6, 0x19],
            is_extended_id=False
        )
        canbus.send_messages(msg)

        microsec_message(5, "Test message processed")

    microsec_message(1, "End of test data feed")
