import simplepyble
import time
import logging

logger = logging.getLogger("BLE")

def get_any_adapter() -> simplepyble.Adapter:
    adapters = simplepyble.Adapter.get_adapters()

    if len(adapters) == 0:
        raise Exception("No BLE adapters found")

    return adapters[0]

def reset_adaptor(adapter: simplepyble.Adapter):
    adapter.power_off()
    time.sleep(1)
    adapter.power_on()

def find_peripherals(address = None, identifier = None, service_id = None, scan_duration: int = 1000) -> list[simplepyble.Peripheral]:
    adapter = get_any_adapter()
    
    adapter.set_callback_on_scan_start(lambda: logging.debug(f"BLE scan started using adaptor: {adapter.identifier()} [{adapter.address()}]."))
    adapter.set_callback_on_scan_stop(lambda: logging.debug("BLE scan complete."))
    adapter.scan_for(scan_duration)
    peripherals = adapter.scan_get_results()

    matches = []
    for p in peripherals:
        if identifier is not None and p.identifier().lower() != identifier.lower():
            continue
        if address is not None and p.address().lower() != address.lower():
            continue
        if service_id is not None and not any([sid.uuid().lower() == service_id.lower() for sid in p.services()]):
            continue
        matches.append(p)
    
    return matches

def list_services(peripheral: simplepyble.Peripheral):
    services = peripheral.services()
    for service in services:
        print(f"Service: {service.uuid()}")
        for characteristic in service.characteristics():
            print(f"    Characteristic: {characteristic.uuid()}")

            capabilities = " ".join(characteristic.capabilities())
            print(f"    Capabilities: {capabilities}")

class BleConnection:
    SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E".lower()
    WRITE_UUID   = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E".lower()
    READ_UUID    = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E".lower()

    def __init__(self, peripheral: simplepyble.Peripheral):
        self.peripheral = peripheral
    
    def connect(self):
        self.peripheral.connect()
        logger.debug("BLE Connected")

    def write(self, data: bytes):
        self.peripheral.write_request(self.SERVICE_UUID, self.WRITE_UUID, data)
        logger.debug(f"Written {data}")

    def disconnect(self):
        self.peripheral.disconnect()
        logger.debug("BLE Disconnected")

def get_connected_ble_device():
    identifier = "DCC Service"
    peripherals = find_peripherals(identifier=identifier)
    if len(peripherals) == 0:
        raise Exception(f"No peripherals found with identifier: {identifier}")
    elif len(peripherals) > 1:
        raise Exception(f"Multiple peripherals found with identifier: {identifier}")
    
    connection = BleConnection(peripherals[0])
    connection.connect()
    return connection

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    import time

    device = get_connected_ble_device()
    try:
        start = time.perf_counter()
        for i in range(10):
            device.write(b"Hello from Python!")
        end = time.perf_counter()
        print(f"Time per write: {(end - start) * 1000 / 10:.4f} ms")

    finally:
        device.disconnect()