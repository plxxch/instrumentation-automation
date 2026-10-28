"""
PyVISA control of the Agilent/Keysight E5061B network analyzer used as a
calibrated RF source.

The lab instrument used a TCPIP SOCKET resource:
    TCPIP0::<hostname>::5025::SOCKET

The source power is set with the E5061B SCPI command
    :SOUR1:POW:GPP <dBm>

Copyright (c) 2023 Pengyu Li
SPDX-License-Identifier: MIT
"""

import pyvisa


class VNASource:
    """Small context-managed wrapper around the VNA source."""

    def __init__(self, address, timeout_ms=5000):
        self.address = address
        self._resource_manager = pyvisa.ResourceManager()
        self._instrument = self._resource_manager.open_resource(address)
        self._instrument.write_termination = "\n"
        self._instrument.read_termination = "\n"
        self._instrument.timeout = timeout_ms

    def idn(self):
        """Return the instrument identification string."""
        return self._instrument.query("*IDN?").strip()

    def set_power_dbm(self, power_dbm):
        """Set the RF source power in dBm."""
        self._instrument.write(":SOUR1:POW:GPP {:g}".format(power_dbm))

    def set_frequency_hz(self, frequency_hz):
        """Set the CW frequency (E5061B channel 1)."""
        self._instrument.write(":SENS1:FREQ:CW {:g}".format(frequency_hz))

    def close(self):
        try:
            self._instrument.close()
        finally:
            self._resource_manager.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
