import xml.etree.ElementTree as ET
import shared_memory

def get_boolean(value_bytes: []) -> bool:
    if value_bytes[0] > 0:
        return True
    else:
        return False


def get_number(value_bytes: [], multiplier, offset, endian: str):
    number = 0

    if endian == 'little':
        for i, value_byte in enumerate(value_bytes):
            number += value_byte * (256**i)
    else:
        pass  # ToDo: add big endian code

    return (number * multiplier) + offset


def parse_message(metric: ET.Element, can_bytes: []) -> None:
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
            shared_memory.clutch_depressed = get_boolean(value_bytes)

    elif metric.attrib['name'] == "rpm":
        shared_memory.eng_rpm = get_number(value_bytes, multiplier, offset, 'little')
        # ToDo: add gear calculator

    elif metric.attrib['name'] == "accelerator":
        shared_memory.pedal_position = get_number(value_bytes, multiplier, offset, 'little')

    elif metric.attrib['name'] == "speed":
        # ToDo: add adjustment code
        shared_memory.speed = get_number(value_bytes, multiplier, offset, 'little')

    elif metric.attrib['name'] == "brake":
        shared_memory.brake_pressure = get_number(value_bytes, multiplier, offset, 'little')


tree = ET.parse('cars/bmw_e87_2004_2006.xml')
root = tree.getroot()

messages = [
    [168, [0x15, 0xc6, 0xfa, 0xc0, 0xfa, 0x1d, 0xcf, 0x02]],
    [170, [0xa7, 0x91, 0x09, 0x6a, 0xc5, 0x3e, 0xa4, 0x4f]],
    [414, [0x00, 0xec, 0xef, 0xfc, 0xfe, 0x41, 0x13, 0xcc]],
    [436, [0x00, 0xd0, 0xe2, 0xf9, 0x06, 0x30, 0xfc, 0x96]],
    ]

for msg in messages:
    # lookup the arbitration id in the xml file
    for child in root:
        if msg[0] == int(child.findall('id')[0].text):
            parse_message(child, msg[1])
            print("Speed: ", shared_memory.speed)
            print("RPM: ", shared_memory.eng_rpm)
            print("Clutch: ", shared_memory.clutch_depressed)
            print("Accelerator: ", shared_memory.pedal_position)
            print("Brake: ", shared_memory.brake_pressure)
