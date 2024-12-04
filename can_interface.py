import platform
import os
import can
import time
import pandas as pd

import shared_memory
import my_logger

from constants import *


class CanInterface:
    bus_vector = None

    @staticmethod
    def calculate_adjusted_speed(dashboard_speed) -> int:
        correction_factor = shared_memory.settings.get_speed_correction_factor()
        return int(dashboard_speed * correction_factor)  # kph

    @staticmethod
    def calculate_gear(speed: int, rpm: int) -> int:
        gearing_factor_values = shared_memory.settings.get_gearing_factor()
        kph_per_thousand_rpm = int(speed / (max(rpm, 1) / 1000))
        gear_number = 0

        for i, gear_factor in enumerate(gearing_factor_values):
            if gear_factor[0] <= kph_per_thousand_rpm <= gear_factor[1]:
                gear_number = i
                break

        return gear_number  # gear number

    def read_test_messages(self):
        test_data_frame = pd.read_csv('test_data.csv')
        last_time_offset = 0

        for i, row in test_data_frame.iterrows():
            if shared_memory.get_run_state() == RUN_STATE_RUNNING:
                # calculate the delay needed
                time_offset = float(row['Time (s)'])

                # we need to allow for the case where the starting offset is not zero
                if i == 0:
                    last_time_offset = time_offset

                time.sleep(time_offset - last_time_offset)
                last_time_offset = time_offset

                my_logger.microsec_message(5, "Test message read")

                dash_speed = int(row['SPEED BMW (kph)'])
                shared_memory.speed = self.calculate_adjusted_speed(dash_speed)
                shared_memory.eng_rpm = int(row['RPM'])

                if not shared_memory.clutch_depressed:
                    shared_memory.pre_calc_gear = self.calculate_gear(
                        speed=shared_memory.speed,
                        rpm=shared_memory.eng_rpm
                    )

                shared_memory.brake_pressure = int(row['BRAKE PRESS (bar)'])

                shared_memory.pedal_position = int(row['Pedal Position (%)'])

                my_logger.microsec_message(5, "Test message processed")

            else:
                break

        my_logger.microsec_message(1, "Test data feed stopped")

    def read_live_messages(self):
        try:
            if platform.system() == 'Windows':
                self.bus_vector = can.interface.Bus(
                    channel='2ABDDE6D', interface='usb2can', dll='/Windows/System32/usb2can.dll', bitrate=100000
                )
            elif platform.system() == 'Linux':
                if shared_memory.settings.get_can_adapter() == "Waveshare":
                    os.system('sudo ip link set can0 down')
                    os.system('sudo ip link set can0 up type can bitrate 100000')
                    self.bus_vector = can.interface.Bus(channel='can0', interface='socketcan')
                else:
                    # ToDo: Merge with above code and eliminate the need for get_can_adapter
                    self.bus_vector = can.interface.Bus(
                        channel='can0', interface='socketcan', bitrate=100000
                )
        except:
            my_logger.microsec_message(1, "Failed to open the interface to the CAN adapter")
            my_logger.microsec_message(1, "Signal to the presentation thread that shutdown is needed")
            shared_memory.set_run_state(RUN_STATE_CAN_INTERFACE_FAILURE)

        if shared_memory.get_run_state() == RUN_STATE_RUNNING:
            with self.bus_vector as bus:

                count = 1
                while shared_memory.get_run_state() == RUN_STATE_RUNNING:
                    for msg in bus:
                        if shared_memory.get_run_state() != RUN_STATE_RUNNING:
                            break

                        # print(count, hex(msg.arbitration_id), msg.data.hex(' ', -4))
                        if msg.arbitration_id == 436:  # 436 (0x1b4) gives speed
                            # (((Byte[1] - 208) * 256) + Byte[0]) / 16 -> gives mph
                            # therefore
                            # (((Byte[1] - 208) * 256) + Byte[0]) / 10 -> gives kph
                            dash_speed = (((int(msg.data[1]) - 208) * 256) + int(msg.data[0])) / 10
                            shared_memory.speed = self.calculate_adjusted_speed(int(dash_speed))
                            # print("Speed (kph): ", dash_speed)

                        elif msg.arbitration_id == 170:  # 170 (0xAA) gives rpm
                            # ((Byte[5] * 256) + Byte[4] ) / 4 -> gives rpm
                            rpm = ((int(msg.data[5]) * 256) + int(msg.data[4])) / 4
                            shared_memory.eng_rpm = int(rpm)
                            # print("Revs (rpm): ", rpm)
                            if not shared_memory.clutch_depressed:
                                shared_memory.pre_calc_gear = self.calculate_gear(
                                speed=shared_memory.speed,
                                rpm=shared_memory.eng_rpm
                                )
                            shared_memory.pedal_position = 100 * int(msg.data[3]) / 254

                        elif msg.arbitration_id == 168:  # 168 (0xA8) contains clutch status
                            if msg.data[5] & 0x01:
                                shared_memory.clutch_depressed = True
                            else:
                                shared_memory.clutch_depressed = False

                        elif msg.arbitration_id == 414:  # 414 (0x19E) contains brake pressure
                            shared_memory.brake_pressure = int(msg.data[6])

                        count += 1

            self.bus_vector.shutdown()
            my_logger.microsec_message(1, "CAN bus interface closed")

    def read_messages(self):
        shared_memory.set_run_state(RUN_STATE_RUNNING)
        my_logger.microsec_message(1, "Backend started")

        if shared_memory.settings.get_test_mode():
            self.read_test_messages()
        else:
            self.read_live_messages()

        shared_memory.set_run_state(RUN_STATE_BACKEND_STOPPED)
        my_logger.microsec_message(1, "Backend thread exiting")
        exit(0)
        
    def kick_backend(self):
        if self.bus_vector:
            my_logger.microsec_message(1, "Give the backend a kick to trigger thread exit")
            # give the can interface a kick in case we don't have incoming messages
            msg = can.Message(arbitration_id=0x2fa, data=[0xff, 0xff, 0xff, 0xff, 0xff], is_extended_id=False)
            try:
                # this may not work if can interface is already shut
                self.bus_vector.send(msg)
            except:
                my_logger.microsec_message(1, "Kicker not needed - backend thread has already exited")


