"""
RF-to-DC efficiency calculation used by the sweep experiments.

    P_out = V^2 / R_load
    P_in  = 10^(P_dbm / 10) mW
    efficiency [%] = P_out / P_in * 100

Copyright (c) 2023 Pengyu Li
SPDX-License-Identifier: MIT
"""


def efficiency_percent(voltage_v, load_ohm, power_dbm):
    """Return RF-to-DC conversion efficiency in percent."""
    if load_ohm <= 0:
        raise ValueError("load_ohm must be positive")
    input_mw = 10.0 ** (power_dbm / 10.0)
    output_mw = (voltage_v ** 2) / load_ohm * 1000.0
    return output_mw / input_mw * 100.0
