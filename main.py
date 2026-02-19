''' TODO: ADD CLI TOOL HERE '''

import ble_comms
from dcc import Accessory

# Controller connections
controller = ble_comms.get_connected_ble_device()
signal = Accessory(controller, 42, ["green", "red", "yellow", "two yellow"])
signal.test()

def main():
    print("Hello from dcc-rail-controller!")


if __name__ == "__main__":
    main()