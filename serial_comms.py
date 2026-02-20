import serial
from serial.tools import list_ports
import logging

logger = logging.getLogger("Serial")

class SerialConnection:
    def __init__(self, peripheral: serial.Serial):
        self.peripheral = peripheral
    
    def connect(self):
        self.peripheral.open()
        logger.debug("Serial Device Connected")

    def write(self, data: bytes):
        # Construct packet with header and checksum
        self.peripheral.write(self._build_packet(data))
        logger.debug(f"Written {data}")

    def _build_packet(self, data: bytes) -> bytes:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("data must be bytes or bytearray")

        length = len(data)
        if length == 0 or length > 0xFFFF:
            raise ValueError("invalid payload length")

        # XOR-16 checksum over payload
        crc = 0
        for b in data:
            crc ^= b

        header = bytes([
            0x10,              # sync byte
            length & 0xFF,     # len_L
            (length >> 8) & 0xFF  # len_H
        ])

        checksum = bytes([
            crc & 0xFF,        # crc_L
            (crc >> 8) & 0xFF  # crc_H (usually 0)
        ])

        return header + data + checksum

    def disconnect(self):
        self.peripheral.close()
        logger.debug("Serial Device Disconnected")

def get_connected_serial_device(comport: str|None = None):
    peripherals = []
    if comport is not None:
        peripherals.append(comport)
    else:
        for port in list_ports.comports():
            if (port.vid == 4292) and (port.pid == 60000):
                peripherals.append(port.device)
        
    if len(peripherals) == 0:
        raise Exception("No matching serial devices found")
    elif len(peripherals) > 1:
        raise Exception(f"Multiple matching serial devices found, please specify a COM port to resolve: {peripherals}")
    
    logger.debug(f'Connecting to serial device: {peripherals[0]}')
    connection = SerialConnection(serial.Serial(peripherals[0], baudrate=115200, timeout=1))
    logger.debug('Connected to serial device')
    return connection

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    dev = get_connected_serial_device()
    dev.write(b'\x01\x02\x03\x04')
    print(dev.peripheral.readline())