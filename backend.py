import platform
import can
import time
import shared_memory


class Backend:
    bus_vector = None

    def __init__(self):
        self.bus_vector = can.interface.Bus(
            bustype="usb2can", channel="2ABDDE6D", bitrate=100000, dll='/Windows/System32/usb2can.dll'
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

        if gear_number == 0:
            stop_here = True

        return gear_number  # gear number

    def get_can_message(self):

        msg = self.bus_vector.recv()
        print(hex(msg.arbitration_id), msg.data.hex(' ', -4))

        return

    def backend_loop(self):
        shared_memory.run_state = shared_memory.RUN_STATE_RUNNING

        while shared_memory.run_state == shared_memory.RUN_STATE_RUNNING:
            self.get_can_message()
            shared_memory.speed = self.calculate_adjusted_speed(52)
            shared_memory.pre_calc_gear = self.calculate_gear(
                speed=shared_memory.speed,
                rpm=shared_memory.eng_rpm
            )
            time.sleep(0.05)

        # shut the usb2can bus
        self.bus_vector.shutdown()

        exit(0)
