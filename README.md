# Instrumentation Automation — RF Measurement and Device Characterization

Python automation for a small RF measurement bench. The scripts orchestrate a
network analyzer, a signal generator, an RF power meter and a Modbus voltage
meter to characterize rectifier / energy-harvesting devices, record the data to
CSV and optionally plot the RF-to-DC efficiency.

The repository is a cleaned, reusable version of the lab scripts used for
power-sweep and efficiency measurements.

## What this repository demonstrates

- **VISA / SCPI instrument control** through PyVISA (TCPIP SOCKET resource).
- **Modbus RTU** communication with a voltage meter over serial.
- **ASCII serial protocols** for a signal generator and a configurable RF
  power meter.
- **Multi-instrument orchestration**: source power, settling, repeated
  measurements, averaging and CSV logging.
- **Clean process control**: CLI configuration, context-managed resources,
  safe source-power reset and error handling.

## Architecture

```
                 SCPI / PyVISA (TCPIP SOCKET)
  ┌────────────┐ ─────────────────────────────┐
  │ VNA        │                              │
  │ E5061B     │                              ▼
  └────────────┘                     ┌─────────────────┐
                                     │  Experiment     │
  ┌────────────┐  ASCII serial       │  script         │──► CSV / plot
  │ Signal     │ ───────────────────►│                 │
  │ generator  │                     └─────────────────┘
  └────────────┘                              ▲
  ┌────────────┐  serial command/regex         │
  │ RF power   │ ──────────────────────────────┘
  │ meter      │
  └────────────┘
  ┌────────────┐  Modbus RTU
  │ Voltage    │ ──────────────────────────────┘
  │ meter      │
  └────────────┘
```

## Supported instruments

| Instrument | Interface | Notes |
|---|---|---|
| Agilent / Keysight **E5061B** VNA | PyVISA TCPIP SOCKET, SCPI | Used as a calibrated RF source; source power via `:SOUR1:POW:GPP <dBm>` |
| ASCII **signal generator** | Serial, 115200 8N1 | `wp00001\n` / `wp00000\n` selects sign; `wv0NNN00\n` sets magnitude |
| Modbus **voltage meter** | Serial, 9600 8N1 | Function 0x03, two registers; second register is voltage in 1 mV counts |
| Serial **RF power meter** | Configurable serial command | Command and numeric-response regex are passed from the CLI because the protocol is board-specific |

The VNA address and every serial port are command-line arguments; nothing is
hard-coded to a particular bench.

## Installation

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
```

PyVISA needs a VISA backend. `pyvisa-py` is installed by default and supports
TCPIP SOCKET resources; if the bench already has NI-VISA or Keysight VISA,
PyVISA can use it instead.

## Experiments

### 1. VNA source + voltage meter → efficiency sweep

```bash
python -m experiments.vna_efficiency_sweep \
    --vna-address "TCPIP0::<hostname>::5025::SOCKET" \
    --voltage-port COM41 \
    --power-min -20 --power-max 10 --power-step 1 \
    --repeats 3 --settle-s 1 \
    --load-ohm 470000 \
    --csv vna_efficiency.csv --plot
```

### 2. Signal generator + voltage meter → efficiency sweep

```bash
python -m experiments.signal_generator_efficiency_sweep \
    --signal-port COM42 --signal-baud 115200 \
    --voltage-port COM40 \
    --power-min -20 --power-max 10 \
    --repeats 3 --load-ohm 3900 \
    --csv signal_generator_efficiency.csv
```

### 3. VNA source + serial RF power meter

```bash
python -m experiments.vna_rf_power_sweep \
    --vna-address "TCPIP0::<hostname>::5025::SOCKET" \
    --power-meter-port COM20 --power-meter-baud 115200 \
    --command-hex "10 02 02 00 02" \
    --csv rf_power_sweep.csv
```

If the power meter returns an ASCII value, omit `--command-hex` and use
`--command "Read\r\n"` plus `--regex`.

### 4. Quick VISA connection check

```bash
python -m experiments.vna_source_check \
    --vna-address "TCPIP0::<hostname>::5025::SOCKET" --power-dbm 0
```

## CSV output

The efficiency sweeps write:

```csv
source,power_dbm,repeat,voltage_v,efficiency_pct
VNA,-20.00,1,0.001234,0.0315
...
```

The RF power sweep writes:

```csv
power_dbm,measured_value,raw_hex
-20.00,0.000012,...
```

## Efficiency calculation

```
P_out = V^2 / R_load
P_in  = 10^(P_dbm / 10)  [mW]
efficiency [%] = P_out / P_in * 100
```

`analysis/efficiency.py` contains the shared calculation.

## Repository layout

```
.
├── instruments/
│   ├── visa_vna.py                  # PyVISA / SCPI E5061B source
│   ├── modbus_voltage_meter.py      # Modbus RTU voltage meter
│   ├── serial_signal_generator.py   # ASCII signal generator
│   └── serial_power_meter.py        # configurable serial power meter
├── experiments/
│   ├── sweep_common.py              # sweep / CSV / plot logic
│   ├── vna_efficiency_sweep.py
│   ├── signal_generator_efficiency_sweep.py
│   ├── vna_rf_power_sweep.py
│   └── vna_source_check.py
├── analysis/
│   └── efficiency.py
├── common/
│   └── modbus.py                    # Modbus CRC and register helpers
├── requirements.txt
└── LICENSE
```

## Notes

- The original lab scripts used hard-coded COM ports and instrument hostnames;
  this version takes them from the command line.
- The RF power meter protocol differs between boards. The wrapper accepts an
  ASCII or hex command and a regex for the numeric response.
- The unused third-party `instr_tests` (GPLv3) package found in the original
  folder is **not** included. The scripts here talk to the instruments directly
  through PyVISA and pyserial.
- The `vna_rf_power_sweep.py` example reflects the commands used with the lab
  power-meter board; verify the command/response format for your own device.

## License

MIT License, Copyright (c) 2023 Pengyu Li. See [LICENSE](LICENSE).
