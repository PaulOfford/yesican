import can
import time

print(f"python-can version: {can.__version__}")

with can.Bus(
    interface="usb2can",
    channel="2ABDDE6D",
    bitrate=100000,
    dll="/Windows/System32/usb2can.dll"
) as bus:

    print(f"Bus opened: {bus.channel_info}")
    print(f"Handle: {bus.handle}")

    time.sleep(1)

    msg = can.Message(
        arbitration_id=0x123,
        data=[0x01, 0x02, 0x03, 0x04],
        is_extended_id=False,
        check=True
    )

    print("Sending message")

    bus.send(msg)

    print("Send accepted by driver")