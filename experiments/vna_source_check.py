#!/usr/bin/env python3
"""
Minimal VISA connection check: identify the VNA and set its source power.

Example:
    python -m experiments.vna_source_check \
        --vna-address "TCPIP0::<host>::5025::SOCKET" --power-dbm 0
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instruments.visa_vna import VNASource


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vna-address", required=True)
    parser.add_argument("--power-dbm", type=float, default=0.0)
    return parser.parse_args()


def main():
    args = parse_args()

    with VNASource(args.vna_address) as vna:
        print("IDN: {}".format(vna.idn()))
        vna.set_power_dbm(args.power_dbm)
        print("Source power set to {:g} dBm".format(args.power_dbm))


if __name__ == "__main__":
    main()
