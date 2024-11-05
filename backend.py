import platform

import can
import time
import shared_memory


class Backend:
    def calculate_adjusted_speed(self, dashboard_speed) -> int:
        correction_factor = shared_memory.settings.get_speed_correction_factor()
        return int(dashboard_speed * correction_factor)  # kph

    def calculate_gear(self, speed: int, rpm: int) -> int:
        gearing_factor_values = shared_memory.settings.get_gearing_factor()
        kph_per_thousand_rpm = int(speed / (rpm / 1000))
        gear_number = 0

        for i, gear_factor in enumerate(gearing_factor_values):
            if kph_per_thousand_rpm >= gear_factor[0] and kph_per_thousand_rpm <= gear_factor[1]:
                gear_number = i
                break

        if gear_number == 0:
            stop_here = True

        return gear_number  # gear number

    def get_can_message(self):
        junk = platform.system()
        _bustype = None
        _channel = None
        _interface =None
        _dll = None

        if platform.system() == 'Linux':
            _channel = 'can0'
            _interface = 'socketcan'
        elif platform.system() == 'Windows':
            _bustype = 'usb2can'
            _channel = '2ABDDE6D'
            _dll = '/Windows/System32/usb2can.dll'

        with can.interface.Bus(
                bustype=_bustype, channel=_channel, interface=_interface, dll=_dll, bitrate=100000
        ) as bus:

            count = 1
            while (True):
                for msg in bus:
                    print(count, hex(msg.arbitration_id), msg.data.hex(' ', -4))

                    count += 1
        return

    def run_backend(self):
        shared_memory.speed = self.calculate_adjusted_speed(52)
        shared_memory.pre_calc_gear = self.calculate_gear(
            speed=shared_memory.speed,
            rpm=shared_memory.eng_rpm
        )
        shared_memory.root.after(100, self.run_backend)
