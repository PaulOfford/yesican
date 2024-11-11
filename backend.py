import platform
import can
import time
import shared_memory
import pandas as pd


class Backend:
    bus_vector = None
    test_data_frame = None
    test_data_index = 0

    def __init__(self):
        if shared_memory.settings.get_test_mode():
            self.test_data_frame = pd.read_csv('test_data.csv')
            pass
        else:
            if shared_memory.is_linux_os:
                self.bus_vector = can.interface.Bus(
                    channel='can0', interface='socketcan', bitrate=100000
                )
            else:
                self.bus_vector = can.interface.Bus(
                    channel='2ABDDE6D', interface='usb2can', dll='/Windows/System32/usb2can.dll', bitrate=100000
                )

    def calculate_adjusted_speed(self, dashboard_speed) -> int:
        correction_factor = shared_memory.settings.get_speed_correction_factor()
        return int(dashboard_speed * correction_factor)  # kph

    def calculate_gear(self, speed: int, rpm: int) -> int:
        gearing_factor_values = shared_memory.settings.get_gearing_factor()
        kph_per_thousand_rpm = int(speed / (max(rpm, 1) / 1000))
        gear_number = 0

        for i, gear_factor in enumerate(gearing_factor_values):
            if kph_per_thousand_rpm >= gear_factor[0] and kph_per_thousand_rpm <= gear_factor[1]:
                gear_number = i
                break

        return gear_number  # gear number

    def get_can_message(self) -> dict:
        message_content = {'canid': 0, 'speed': 0, 'rpm': 0}
        if shared_memory.settings.get_test_mode():
            row = self.test_data_frame.iloc[self.test_data_index]
            message_content['speed'] = row['SPEED BMW (kph)']
            message_content['rpm'] = row['RPM']
            self.test_data_index += 1
        else:
            msg = self.bus_vector.recv()
            if msg.arbitration_id == 436:  # 436 (0x1b4) gives speed
                message_content['canid'] = msg.arbitration_id
                # (((Byte[1] - 208) * 256) + Byte[0]) / 16 -> gives mph
                # therefore
                # (((Byte[1] - 208) * 256) + Byte[0]) / 10 -> gives kph
                message_content['speed'] = (((int(msg.data[1]) - 208) * 256) + int(msg.data[0])) / 10
                # print("Speed (kph): ", message_content['speed'])

            elif msg.arbitration_id == 170:  # 170 (0xAA) gives rpm
                message_content['canid'] = msg.arbitration_id
                # ((Byte[5] * 256) + Byte[4] ) / 4 -> gives rpm
                message_content['rpm'] = ((int(msg.data[5]) * 256) + int(msg.data[4])) / 4
                # print("Revs (rpm): ", message_content['rpm'])

        return message_content

    def backend_loop(self):
        shared_memory.run_state = shared_memory.RUN_STATE_RUNNING

        while shared_memory.run_state == shared_memory.RUN_STATE_RUNNING:
            message_values = self.get_can_message()
            if message_values['canid'] == 436:
                shared_memory.speed = self.calculate_adjusted_speed(int(message_values['speed']))
            elif message_values['canid'] == 170:
                shared_memory.eng_rpm = int(message_values['rpm'])
            shared_memory.pre_calc_gear = self.calculate_gear(
                speed=shared_memory.speed,
                rpm=shared_memory.eng_rpm
            )
            time.sleep(0.05)

        if shared_memory.settings.get_test_mode() == False:
            # shut the usb2can bus
            self.bus_vector.shutdown()

        exit(0)
