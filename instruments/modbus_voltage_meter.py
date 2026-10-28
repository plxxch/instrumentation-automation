"""
Modbus RTU voltage meter used to measure the rectifier / DUT output voltage.

Prototype settings:
    9600 8N1, slave 1, function 0x03, two holding registers
    request: 01 03 00 00 00 02 C4 0B
    the second register is the voltage in 1 mV counts

Copyright (c) 2023 Pengyu Li
SPDX-License-Identifier: MIT
"""

import serial

from common.modbus import decode_u16, read_holding_registers


class ModbusVoltageMeter:
    def __init__(
        self,
        port,
        baudrate=9600,
        slave=1,
        register=1,
        scale=0.001,
        timeout=1.0,
    ):
        self.slave = slave
        self.register = register
        self.scale = scale
        self.timeout = timeout
        self._port = serial.Serial(port, baudrate, timeout=timeout)

    def read_voltage(self):
        """Return the voltage in volts, or None if the response is invalid."""
        data = read_holding_registers(
            self._port,
            slave=self.slave,
            start=0,
            count=max(2, self.register + 1),
            timeout=self.timeout,
        )
        value = decode_u16(data, 2 * self.register)
        if value is None:
            return None
        return value * self.scale

    def close(self):
        self._port.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
