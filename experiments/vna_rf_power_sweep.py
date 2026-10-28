#!/usr/bin/env python3
"""
Sweep the VNA source power and read a serial RF power meter.

The power meter command/response format is device-specific; pass the command
and a regular expression for the numeric reading, or use --command-hex.

Example:
    python -m experiments.vna_rf_power_sweep \
        --vna-address "TCPIP0::<host>::5025::SOCKET" \
        --power-meter-port COM20 --power-meter-baud 115200 \
        --command-hex "10 02 02 00 02" --regex "[-+]?\\d+(?:\\.\\d+)?" \
        --csv rf_power_sweep.csv
"""

import argparse
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experiments.sweep_common import power_list
from instruments.serial_power_meter import SerialPowerMeter
from instruments.visa_vna import VNASource


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vna-address", required=True)
    parser.add_argument("--power-meter-port", required=True)
    parser.add_argument("--power-meter-baud", type=int, default=921600)
    parser.add_argument("--command", default="Read\r\n", help="ASCII command")
    parser.add_argument("--command-hex", help="hex command (overrides --command)")
    parser.add_argument("--init-command-hex", help="optional initialization hex command")
    parser.add_argument("--regex", default=r"[-+]?\d+(?:\.\d+)?")
    parser.add_argument("--power-min", type=float, default=-20.0)
    parser.add_argument("--power-max", type=float, default=10.0)
    parser.add_argument("--power-step", type=float, default=1.0)
    parser.add_argument("--settle-s", type=float, default=1.0)
    parser.add_argument("--safe-power-dbm", type=float, default=0.0)
    parser.add_argument("--csv", default="rf_power_sweep.csv")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.command_hex:
        command = bytes.fromhex(args.command_hex)
    else:
        command = args.command.encode("ascii")

    directory = os.path.dirname(os.path.abspath(args.csv))
    if directory:
        os.makedirs(directory, exist_ok=True)

    with VNASource(args.vna_address) as vna:
        with SerialPowerMeter(
            args.power_meter_port,
            baudrate=args.power_meter_baud,
            command=command,
            regex=args.regex,
        ) as meter:
            print("VNA: {}".format(vna.idn()))
            if args.init_command_hex:
                meter.write_hex(args.init_command_hex)

            handle = open(args.csv, "w", newline="", encoding="utf-8")
            writer = csv.writer(handle)
            writer.writerow(["power_dbm", "measured_value", "raw_hex"])

            try:
                for power in power_list(
                    args.power_min, args.power_max, args.power_step
                ):
                    vna.set_power_dbm(power)
                    time.sleep(max(0.0, args.settle_s))

                    value, raw = meter.read()
                    writer.writerow(
                        [
                            "{:.2f}".format(power),
                            "" if value is None else "{:.6f}".format(value),
                            raw.hex(),
                        ]
                    )
                    handle.flush()
                    print(
                        "power={:+.1f} dBm  reading={}  raw={}".format(
                            power,
                            "n/a" if value is None else "{:.6f}".format(value),
                            raw.hex(),
                        )
                    )
            finally:
                handle.close()
                try:
                    vna.set_power_dbm(args.safe_power_dbm)
                except Exception:
                    pass


if __name__ == "__main__":
    main()
