"""
Configurable serial RF power meter.

The exact command/response format depends on the power-meter board. This
wrapper lets the experiment specify the command (ASCII or hex) and a regular
expression for extracting the numeric reading from the response, so it can be
adapted without rewriting the experiment.

Example:
    SerialPowerMeter("COM37", 921600, command=b"Read\\r\\n",
                     regex=r"[-+]?\\d+(?:\\.\\d+)?")
"""

import re
import time

import serial


class SerialPowerMeter:
    def __init__(
        self,
        port,
        baudrate=921600,
        command=b"Read\r\n",
        timeout=1.0,
        encoding="ascii",
        regex=r"[-+]?\d+(?:\.\d+)?",
    ):
        self._port = serial.Serial(port, baudrate, timeout=timeout)
        self.command = command
        self.encoding = encoding
        self.regex = re.compile(regex)

    def write_hex(self, command_hex):
        """Send a hex command such as '10 02 02 00 02'."""
        self._port.write(bytes.fromhex(command_hex))
        self._port.flush()

    def read(self):
        """Send the configured command and return (value, raw_bytes)."""
        self._port.reset_input_buffer()
        if self.command:
            self._port.write(self.command)
            self._port.flush()

        time.sleep(0.05)
        raw = self._port.read(256)
        text = raw.decode(self.encoding, errors="replace")
        match = self.regex.search(text)
        value = float(match.group(0)) if match else None
        return value, raw

    def close(self):
        self._port.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
