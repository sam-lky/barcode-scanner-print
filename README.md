# Barcode Scanner & Label Printer

A desktop GUI application for scanning barcodes and printing carton labels via a TSC TTP-244 Pro thermal label printer. Built for use in a live warehouse and manufacturing environment.

Operators scan items one at a time into a batch, then print a single carton label listing all serial numbers in the batch, alongside a QR code, carton ID, and timestamp. Developed during an internship at Hope Technik.

---

## Architecture

```
barcode-scanner-print/
├── scanner_printer_gui.py   # Main GUI application (Tkinter)
├── tsc_printer.py           # TSC printer interface — serial comms via TSPL commands
├── print_tspl.py            # Standalone TSPL print script (testing/dev utility)
├── carton_counter.txt       # Persistent carton counter (auto-managed by app)
└── requirements.txt
```

---

## Features

- **Batch scanning** — scan multiple items sequentially; each barcode is parsed and queued before printing
- **S/N extraction** — automatically extracts serial numbers from raw barcode strings using regex (handles multi-field barcode formats like `EBD S/N: HAA02-2544-336PCB S/No: ...`)
- **Carton label printing** — generates a structured 100×150mm label with:
  - Auto-formatted Carton ID (`CYYWW-XXX` format, e.g. `C2544-001`)
  - Date packed timestamp
  - QR code of Carton ID
  - Table of all scanned serial numbers
- **Persistent counter** — carton counter saved to disk between sessions (`carton_counter.txt`)
- **Override mode** — manually override Carton ID or date for reprints and corrections
- **Threaded printing** — print jobs run in background thread to keep UI responsive
- **Right-click delete** — remove individual scanned items from batch before printing

---

## Tech Stack

| Component | Technology |
|---|---|
| GUI | Python · Tkinter |
| Printer communication | `pyserial` — serial interface (TSPL commands) |
| Barcode parsing | Python `re` — regex-based S/N extraction |
| Label format | TSPL (TSC Printer Language) |
| Platform | Windows (COM port serial) |

---

## Hardware Requirements

- **Printer:** TSC TTP-244 Pro thermal label printer
- **Connection:** USB-to-serial (COM port)
- **Label size:** 100mm × 150mm (configurable in `scanner_printer_gui.py`)
- **Scanner:** Any USB HID barcode/QR scanner (sends keystrokes + Enter)

---

## Getting Started

### Prerequisites

- Python 3.8+
- Windows OS (COM port required for printer)
- TSC TTP-244 Pro connected via USB

### Installation

```bash
git clone https://github.com/sam-lky/barcode-scanner-print.git
cd barcode-scanner-print

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

### Configure

In `scanner_printer_gui.py`, the default COM port is `COM10` and baudrate is `9600`. You can change these at runtime via the Settings panel in the GUI, or update the defaults:

```python
self.port = "COM10"      # Change to your printer's COM port
self.baudrate = 9600
```

### Run

```bash
python scanner_printer_gui.py
```

---

## Usage

1. Launch the app — scanner input field is auto-focused
2. Scan items with a USB barcode scanner (or type manually + Enter)
3. Each scan extracts and queues the serial number
4. Right-click any item in the list to remove it
5. Click **PRINT LABEL** when the batch is ready
6. The app prints the carton label and prompts to start the next batch

---

## Label Format

```
┌─────────────────────────────────────────┐
│ Carton ID: C2544-001          [QR Code] │
│ Date Packed: 2025-11-04       14:32:00  │
├─────────────────────────────────────────┤
│ 01. HAA02-2544-336   02. HAA02-2544-337 │
│ 03. HAA02-2544-338   04. HAA02-2544-339 │
│ ...                                     │
└─────────────────────────────────────────┘
```

---

## Related

- [EDB Inventory Management System](https://github.com/sam-lky/EDB-inventory-management) — the inventory backend this tool was built alongside
