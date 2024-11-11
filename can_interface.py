import platform
import shared_memory
import can


class CanInterface:
    bus_vector = None

    def calculate_adjusted_speed(self, dashboard_speed) -> int:
        correction_factor = shared_memory.settings.get_speed_correction_factor()
        return int(dashboard_speed * correction_factor)  # kph

    def calculate_gear(self, speed: int, rpm: int) -> int:
        gearing_factor_values = shared_memory.settings.get_gearing_factor()
        kph_per_thousand_rpm = int(speed / (max(rpm, 1) / 1000))
        gear_number = 0

        for i, gear_factor in enumerate(gearing_factor_values):
            if gear_factor[0] <= kph_per_thousand_rpm <= gear_factor[1]:
                gear_number = i
                break

        return gear_number  # gear number

    def read_messages(self):
        shared_memory.run_state = shared_memory.RUN_STATE_RUNNING

        try:
            if platform.system() == 'Windows':
                shared_memory.bus_vector = can.interface.Bus(
                    channel='2ABDDE6D', interface='usb2can', dll='/Windows/System32/usb2can.dll', bitrate=100000
                )
            elif platform.system() == 'Linux':
                shared_memory.bus_vector = can.interface.Bus(
                    channel='can0', interface='socketcan', bitrate=100000
                )
        except:
            print("Failed to open the interface to the USB2CAN adapter")
            shared_memory.run_state = shared_memory.RUN_STATE_CAN_INTERFACE_FAILURE

        if shared_memory.run_state == shared_memory.RUN_STATE_RUNNING:
            with shared_memory.bus_vector as bus:

                count = 1
                while shared_memory.run_state == shared_memory.RUN_STATE_RUNNING:
                    for msg in bus:
                        if shared_memory.run_state != shared_memory.RUN_STATE_RUNNING:
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
                            shared_memory.pre_calc_gear = self.calculate_gear(
                                speed=shared_memory.speed,
                                rpm=shared_memory.eng_rpm
                        )

                        count += 1

            if not shared_memory.settings.get_test_mode():
                # shut the usb2can bus
                shared_memory.bus_vector.shutdown()
                print("CAN bus interface closed")

        exit(0)
