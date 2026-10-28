#!/usr/bin/env python3
"""
Sweep the ASCII serial signal generator and measure the DUT output voltage
with a Modbus voltage meter.

Example:
    python -m experiments.signal_generator_efficiency_sweep \
        --signal-port COM42 --voltage-port COM40 --load-ohm 3900 \
        --power-min -20 --power-max 10 --csv signal_generator_sweep.csv
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.sweep_common import add_sweep_arguments, run_efficiency_sweep
from instruments.modbus_voltage_meter import ModbusVoltageMeter
from instruments.serial_signal_generator import SerialSignalGenerator


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--signal-port", required=True, help="signal generator serial port")
    parser.add_argument("--signal-baud", type=int, default=115200)
    parser.add_argument("--voltage-port", required=True, help="voltage meter serial port")
    parser.add_argument("--voltage-baud", type=int, default=9600)
    parser.add_argument("--voltage-slave", type=int, default=1)
    parser.add_argument("--voltage-register", type=int, default=1)
    parser.add_argument("--voltage-scale", type=float, default=0.001)
    add_sweep_arguments(parser, default_load_ohm=3900.0)
    return parser.parse_args()


def main():
    args = parse_args()

    with SerialSignalGenerator(args.signal_port, baudrate=args.signal_baud) as generator:
        with ModbusVoltageMeter(
            args.voltage_port,
            baudrate=args.voltage_baud,
            slave=args.voltage_slave,
            register=args.voltage_register,
            scale=args.voltage_scale,
        ) as meter:
            try:
                run_efficiency_sweep(
                    args,
                    "Signal generator",
                    generator.set_output_dbm,
                    meter.read_voltage,
                )
            finally:
                try:
                    generator.set_output_dbm(0)
                except Exception:
                    pass


if __name__ == "__main__":
    main()
