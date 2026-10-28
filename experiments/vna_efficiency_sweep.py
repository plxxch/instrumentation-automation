#!/usr/bin/env python3
"""
Sweep the VNA source power and measure the DUT output voltage with a Modbus
voltage meter. Results are written to CSV, optionally plotted.

Example:
    python -m experiments.vna_efficiency_sweep \
        --vna-address "TCPIP0::<host>::5025::SOCKET" \
        --voltage-port COM41 --load-ohm 470000 \
        --power-min -20 --power-max 10 --csv vna_sweep.csv --plot
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.sweep_common import add_sweep_arguments, run_efficiency_sweep
from instruments.modbus_voltage_meter import ModbusVoltageMeter
from instruments.visa_vna import VNASource


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vna-address", required=True, help="PyVISA resource string")
    parser.add_argument("--voltage-port", required=True, help="voltage meter serial port")
    parser.add_argument("--voltage-baud", type=int, default=9600)
    parser.add_argument("--voltage-slave", type=int, default=1)
    parser.add_argument("--voltage-register", type=int, default=1)
    parser.add_argument("--voltage-scale", type=float, default=0.001)
    parser.add_argument("--safe-power-dbm", type=float, default=0.0)
    add_sweep_arguments(parser, default_load_ohm=470000.0)
    return parser.parse_args()


def main():
    args = parse_args()

    with VNASource(args.vna_address) as vna:
        with ModbusVoltageMeter(
            args.voltage_port,
            baudrate=args.voltage_baud,
            slave=args.voltage_slave,
            register=args.voltage_register,
            scale=args.voltage_scale,
        ) as meter:
            print("VNA: {}".format(vna.idn()))
            try:
                run_efficiency_sweep(
                    args,
                    "VNA",
                    vna.set_power_dbm,
                    meter.read_voltage,
                )
            finally:
                try:
                    vna.set_power_dbm(args.safe_power_dbm)
                except Exception:
                    pass


if __name__ == "__main__":
    main()
