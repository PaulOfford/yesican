import platform
import subprocess
import can
import time
import pandas as pd
import xml.etree.ElementTree as ET

import shared_memory
from my_logger import microsec_message

from constants import *


class CanInterface:
    bus_vector = None
    chan_id = None

    fuel_a = 0
    fuel_b = 0

    @staticmethod
    def get_bus_windows(chan_id, rate, is_listen_only, is_loopback, is_one_shot, filters):

        options = 0
        if is_listen_only:
            options = options | 1
        if is_loopback:
            options = options | 2
        if is_one_shot:
            options = options | 4

        dll_path = '/Windows/System32/usb2can.dll'

        bus = can.interface.Bus(interface="usb2can", channel=chan_id, bitrate=rate, dll=dll_path,
                                flags=options, can_filters=filters)

        return bus

    @staticmethod
    def get_bus_linux(chan_id, rate, is_listen_only, is_loopback, is_one_shot, filters=None):

        listen_only_on_off = "on" if is_listen_only else "off"
        loopback_on_off = "on" if is_loopback else "off"
        oneshot_on_off = "on" if is_one_shot else "off"
        subprocess.run(['ip',  'link',  'set',  'down', chan_id])
        subprocess.run(['ip', 'link', 'set', chan_id, 'type', 'can', 'bitrate', str(rate), 'listen-only',
                        listen_only_on_off, 'loopback', loopback_on_off, 'one-shot', oneshot_on_off])
        subprocess.run(['ip', 'link', 'set', 'up', chan_id])
        bus = can.interface.Bus(interface="socketcan", channel=chan_id, can_filters=filters)  # socketcan bus iface

        return bus

    def open_interface(self, bus, chan_id, rate, is_listen_only=False, is_loopback=False, is_one_shot=False):

        if bus is not None:
            bus.shutdown()

        self.chan_id = chan_id

        try:
            if platform.system() == 'Windows':
                self.bus_vector = self.get_bus_windows(
                                        chan_id=chan_id,
                                        rate=rate,
                                        is_listen_only=is_listen_only,
                                        is_loopback=is_loopback,
                                        is_one_shot=is_one_shot,
                                        filters=None
                )  # we can let most values default
            elif platform.system() == 'Linux':
                self.bus_vector = self.get_bus_linux(
                                        chan_id=shared_memory.settings.get_can_adapter(),
                                        rate=shared_memory.settings.get_can_rate(),
                                        is_listen_only=is_listen_only,
                                        is_loopback=is_loopback,
                                        is_one_shot=is_one_shot,
                                        filters=None
                )  # we can let most values default

        except:
            # except (ValueError, can.exceptions.CanInitializationError, can.exceptions.CanInterfaceNotImplementedError):
            microsec_message(1, "Failed to open the interface to the CAN adapter")
            microsec_message(1, "Signal to the presentation thread that shutdown is needed")
            shared_memory.set_run_state(RUN_STATE_CAN_INTERFACE_FAILURE)

        return self.bus_vector

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

                microsec_message(5, "Test message read")

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

                if shared_memory.pending_race_start:
                    shared_memory.starting_fuel_level = int(row['Fuel Level (l)'])
                    shared_memory.race_start_time = int(time.time())
                    microsec_message(1, f"Race start time set to {shared_memory.race_start_time}")
                    shared_memory.fuel_burn_rate = shared_memory.settings.get_default_consumption_lpm()
                    shared_memory.pending_race_start = False

                shared_memory.current_fuel_level = int(row['Fuel Level (l)'])

                microsec_message(5, "Test message processed")

            else:
                break

        microsec_message(1, "Test data feed stopped")

    @staticmethod
    def get_boolean(value_bytes: []) -> bool:
        if value_bytes[0] > 0:
            return True
        else:
            return False

    @staticmethod
    def get_number(value_bytes: [], multiplier, offset, endian: str):
        number = 0

        if endian == 'little':
            for i, value_byte in enumerate(value_bytes):
                number += value_byte * (256 ** i)
        else:
            pass  # ToDo: add big endian code

        return (number * multiplier) + offset

    def parse_message(self, metric: ET.Element, can_bytes: []) -> None:
        mask = []
        field_length = round((len(metric.findall('bit_mask')[0].text) - 2) / 2)
        field_offset = int(metric.findall('field_offset')[0].text)
        value_bytes = can_bytes[field_offset:field_offset + field_length]

        mask_characters = metric.findall('bit_mask')[0].text
        i = 2
        while i < len(mask_characters):
            mask.append(int(metric.findall('bit_mask')[0].text[i:i + 2], 16))
            i += 2

        for i in range(len(value_bytes)):
            value_bytes[i] &= mask[i]

        multiplier = float(metric.findall('multiplier')[0].text)
        offset = float(metric.findall('offset')[0].text)

        if metric.findall('units')[0].text == 'boolean':
            if metric.attrib['name'] == "clutch":
                shared_memory.clutch_depressed = self.get_boolean(value_bytes)

        elif metric.attrib['name'] == "rpm":
            shared_memory.eng_rpm = self.get_number(value_bytes, multiplier, offset, 'little')

            if not shared_memory.clutch_depressed:
                shared_memory.pre_calc_gear = self.calculate_gear(
                    speed=shared_memory.speed,
                    rpm=shared_memory.eng_rpm
                )

        elif metric.attrib['name'] == "accelerator":
            shared_memory.pedal_position = self.get_number(value_bytes, multiplier, offset, 'little')

        elif metric.attrib['name'] == "speed":
            dash_speed = self.get_number(value_bytes, multiplier, offset, 'little')
            shared_memory.speed = self.calculate_adjusted_speed(dash_speed)

        elif metric.attrib['name'] == "brake":
            shared_memory.brake_pressure = self.get_number(value_bytes, multiplier, offset, 'little')

        elif metric.attrib['name'] == "fuel-a":
            self.fuel_a = self.get_number(value_bytes, multiplier, offset, 'little')

        elif metric.attrib['name'] == "fuel-b":
            self.fuel_b = self.get_number(value_bytes, multiplier, offset, 'little')
            shared_memory.current_fuel_level = self.fuel_a + self.fuel_b
            self.fuel_a, self.fuel_b = 0

    def read_live_messages(self) -> None:
        xml_file_path = "cars/" + shared_memory.settings.get_canbus_codes()
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        if shared_memory.get_run_state() == RUN_STATE_RUNNING:
            with self.bus_vector as bus:
                while shared_memory.get_run_state() == RUN_STATE_RUNNING:
                    for msg in bus:
                        if shared_memory.get_run_state() != RUN_STATE_RUNNING:
                            break

                        # lookup the arbitration id in the xml file
                        for i, child in enumerate(root):
                            if msg.arbitration_id == int(child.findall('id')[0].text):
                                # convert the msg.data from a byte array to a list and then parse
                                self.parse_message(child, list(msg.data))

                                if shared_memory.pending_race_start and shared_memory.current_fuel_level > 0:
                                    shared_memory.starting_fuel_level = shared_memory.current_fuel_level
                                    shared_memory.race_start_time = int(time.time())
                                    shared_memory.pending_race_start = False
                                    microsec_message(1, f"Race start time set to {shared_memory.race_start_time}")

            self.bus_vector.shutdown()
            microsec_message(1, "CAN bus interface closed")

    def read_messages(self):
        shared_memory.set_run_state(RUN_STATE_RUNNING)
        microsec_message(1, "Backend started")

        if shared_memory.settings.get_test_mode():
            self.read_test_messages()
        else:
            self.read_live_messages()

        shared_memory.set_run_state(RUN_STATE_BACKEND_STOPPED)
        microsec_message(1, "Backend thread exiting")
        exit(0)

    def send_messages(self, message):
        self.bus_vector.send(message)
        microsec_message(5, str(message))

    def kick_backend(self):
        if self.bus_vector:
            microsec_message(1, "Give the backend a kick to trigger thread exit")
            # give the can interface a kick in case we don't have incoming messages
            msg = can.Message(arbitration_id=0x2fa, data=[0xff, 0xff, 0xff, 0xff, 0xff], is_extended_id=False)
            try:
                # this may not work if the CAN interface is already shut
                self.bus_vector.send(msg)
            except:
                #  except can.exceptions.CanOperationError:
                microsec_message(1, "Kicker not needed - backend thread has already exited")
