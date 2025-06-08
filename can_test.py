from can_interface import CanInterface
from settings_code import Settings


if __name__ == "__main__":
    canbus = None
    settings = Settings()
    interface = CanInterface()
    canbus = interface.open_interface(
        canbus,
        settings.get_can_adapter(),
        settings.get_can_rate()
    )

    with canbus as bus:
        count = 1
        while True:
            for msg in bus:
                print(count, hex(msg.arbitration_id), msg.data.hex(' ', -4))

                count += 1
