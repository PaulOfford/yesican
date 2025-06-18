import platform
import can
import os
import time
import pandas as pd

from can_interface import CanInterface
from settings_code import Settings
from my_logger import microsec_message

settings = Settings()


if __name__ == "__main__":
    canbus = None
    interface = CanInterface()
    canbus = interface.open_interface(
        canbus,
        settings.get_can_send_adapter(),
        settings.get_can_rate()
    )
    microsec_message(1, "CAN bus interface open")

    test_data_frame = pd.read_csv('test_data.csv')
    microsec_message(1, "Test data loaded")

    last_time_offset = 0
    microsec_message(1, "Send starting")

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
        test_msg = can.Message(
            arbitration_id=0x1b4,
            data=[byte0, byte1, 0xe2, 0xf4, 0x16, 0x30, 0xfc, 0xa1],
            is_extended_id=False
        )
        interface.send_messages(test_msg)

        # msg.arbitration_id == 170 - Pedal Position
        # byte 3
        pedal_position = float(row['Pedal Position (%)'])
        # there's a bug in the Aim device - it assumes max value is 256 (?) when it's actually 254
        byte3 = int(256 * pedal_position / 100)

        # msg.arbitration_id == 170 - RPM
        # multiply by 4
        # and then place in data byte 4 & 5, little endian
        eng_rpm = int(row['RPM']) * 4
        byte5 = int(eng_rpm/256)
        byte4 = eng_rpm - (byte5 * 256)

        msg = can.Message(
            arbitration_id=0x0aa,
            data=[0x67, 0x32, 0xa0, byte3, byte4, byte5, 0x00, 0x00],
            is_extended_id=False
        )
        interface.send_messages(msg)

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
        interface.send_messages(msg)

        # msg.arbitration_id == 841 - fuel level
        # * get the litre value
        # * convert to a CAN value using fuel.lut
        # * split it 40/60 between fuel_left and fuel_right
        # * place fuel_left in data byte 0 & 1, little endian
        # * place fuel_right in data byte 0 & 1, little endian
        fuel_litres = int(row['Fuel Level (l)'])
        can_total = interface.get_fuel_can_value()
        fuel_left = can_total * 0.4
        fuel_right = can_total - fuel_left

        byte1 = int(fuel_left/256)
        byte0 = fuel_left - (byte1 * 256)

        byte3 = int(fuel_right / 256)
        byte2 = fuel_right - (byte1 * 256)

        test_msg = can.Message(
            arbitration_id=0x349,
            data=[byte0, byte1, byte2, byte3],
            is_extended_id=False
        )
        interface.send_messages(test_msg)

        if i % 10 == 0:
            microsec_message(1, "Test records processed: " + str(i))

        microsec_message(5, "Test message processed")

    microsec_message(1, "End of test data feed")
    microsec_message(1, "Test records processed: " + str(i))

