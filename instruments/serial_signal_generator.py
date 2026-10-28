"""
ASCII serial signal generator used in the lab prototype.

The generator accepts two short ASCII commands:
    wp00001\n   positive output (wp00000 for negative)
    wv0NNN00\n  magnitude in the instrument's native units
                (for example wv00500 for 5 dBm, wv02000 for 20 dBm)

Copyright (c) 2023 Pengyu Li
SPDX-License-Identifier: MIT
"""

import serial


class SerialSignalGenerator:
    def __init__(self, port, baudrate=115200, timeout=1.0):
        self._port = serial.Serial(port, baudrate, timeout=timeout)

    def set_output_dbm(self, power_dbm):
        """Set the output power in dBm (sign + magnitude commands)."""
        magnitude = abs(int(round(power_dbm)))
        if magnitude > 99:
            raise ValueError("power magnitude must be 0..99 in this protocol")

        sign = "wp00001\n" if power_dbm >= 0 else "wp00000\n"
        value = "wv0{:02d}00\n".format(magnitude)

        self._port.write(sign.encode("ascii"))
        self._port.write(value.encode("ascii"))
        self._port.flush()

    def close(self):
        self._port.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
