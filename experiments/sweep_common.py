"""
Shared sweep/CSV/plot logic for the efficiency experiments.

Copyright (c) 2023 Pengyu Li
SPDX-License-Identifier: MIT
"""

import csv
import os
import time

from analysis.efficiency import efficiency_percent


def add_sweep_arguments(parser, default_load_ohm):
    parser.add_argument("--power-min", type=float, default=-20.0)
    parser.add_argument("--power-max", type=float, default=10.0)
    parser.add_argument("--power-step", type=float, default=1.0)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--settle-s", type=float, default=1.0)
    parser.add_argument("--sample-interval-s", type=float, default=0.1)
    parser.add_argument("--load-ohm", type=float, default=default_load_ohm)
    parser.add_argument("--csv", default="efficiency_sweep.csv")
    parser.add_argument("--plot", action="store_true")
    parser.add_argument("--plot-file", help="save the plot instead of showing it")


def power_list(start, stop, step):
    if step <= 0:
        raise ValueError("power step must be positive")
    count = int(round((stop - start) / step)) + 1
    return [round(start + i * step, 6) for i in range(count)]


def run_efficiency_sweep(args, source_name, set_power, read_voltage):
    """Sweep source power, read the DUT voltage and record efficiency."""
    directory = os.path.dirname(os.path.abspath(args.csv))
    if directory:
        os.makedirs(directory, exist_ok=True)

    handle = open(args.csv, "w", newline="", encoding="utf-8")
    writer = csv.writer(handle)
    writer.writerow(
        ["source", "power_dbm", "repeat", "voltage_v", "efficiency_pct"]
    )

    summary = []
    interval = max(0.0, getattr(args, "sample_interval_s", 0.1))
    repeats = max(1, args.repeats)

    try:
        for power in power_list(args.power_min, args.power_max, args.power_step):
            set_power(power)
            time.sleep(max(0.0, args.settle_s))

            voltages = []
            for repeat in range(repeats):
                voltage = read_voltage()
                if voltage is None:
                    print("power={:+.1f} dBm: no valid voltage reading".format(power))
                    continue

                efficiency = efficiency_percent(voltage, args.load_ohm, power)
                voltages.append(voltage)
                writer.writerow(
                    [
                        source_name,
                        "{:.2f}".format(power),
                        repeat + 1,
                        "{:.6f}".format(voltage),
                        "{:.4f}".format(efficiency),
                    ]
                )
                print(
                    "{:<16} power={:+.1f} dBm  V={:.6f} V  eff={:.2f} %".format(
                        source_name, power, voltage, efficiency
                    )
                )
                if interval:
                    time.sleep(interval)

            if voltages:
                average = sum(voltages) / len(voltages)
                summary.append(
                    (power, average, efficiency_percent(average, args.load_ohm, power))
                )
            handle.flush()
    finally:
        handle.close()

    if args.plot:
        plot_summary(summary, args.plot_file)

    return summary


def plot_summary(summary, plot_file=None):
    if not summary:
        print("Nothing to plot")
        return

    import matplotlib.pyplot as plt

    powers = [row[0] for row in summary]
    efficiencies = [row[2] for row in summary]

    plt.figure()
    plt.plot(powers, efficiencies, "o-")
    plt.xlabel("Source power (dBm)")
    plt.ylabel("Efficiency (%)")
    plt.grid(True)
    plt.title("RF-to-DC efficiency")
    plt.tight_layout()

    if plot_file:
        plt.savefig(plot_file, dpi=150)
        print("Plot saved to {}".format(plot_file))
    else:
        plt.show()
