import platform
import os
import can
import time
import pandas as pd
import xml.etree.ElementTree as ET

import shared_memory
import my_logger

from constants import *


class CanInterface:
    bus_vector = None

    def __init__(self):
        xml_file_path = "cars/" + shared_memory.settings.get_canbus_codes()
        self.tree = ET.parse(xml_file_path)
        root = self.tree.getroot()
        for child in root:
            print(child.tag, child.attrib)
            for grandchild in child:
                print(grandchild.tag, grandchild.attrib)
        specs = root.findall('gpi_spec')
        print(specs)
        pass

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

    def read_live_messages(self) -> None:
        try:
            if platform.system() == 'Windows':
                self.bus_vector = can.interface.Bus(
                    channel='2ABDDE6D', interface='usb2can', dll='/Windows/System32/usb2can.dll', bitrate=100000
                )
            elif platform.system() == 'Linux':
                os.system('sudo ip link set can0 down')
                os.system('sudo ip link set can0 up type can bitrate 100000')
                self.bus_vector = can.interface.Bus(channel='can0', interface='socketcan')
        except:
            my_logger.microsec_message(1, "Failed to open the interface to the CAN adapter")
            my_logger.microsec_message(1, "Signal to the presentation thread that shutdown is needed")
            shared_memory.set_run_state(RUN_STATE_CAN_INTERFACE_FAILURE)

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
                                self.parse_message(child, msg)

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
