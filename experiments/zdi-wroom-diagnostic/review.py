"""Offline review of the operator-confirmed four-probe ZDI capture.

Reads only archived files. Creates a new JSON report without overwriting files.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
import sys


ROOT = Path(sys.argv[1]).resolve(strict=True)
META = json.loads((ROOT / "result.json").read_text())
CAPTURE = ROOT / "FP-001.bin"
RATE = 24_000_000
OFFSETS = [-120, -24, 0, 24, 120]
TX_CLOCKS = list(range(9)) + [17, 26, 35, 44]  # Zero-based clock indices.
READ_STARTS = [9, 18, 27, 36]
READINGS = META["phases"][0]["readings"]
DATA = np.memmap(CAPTURE, dtype=np.uint8, mode="r")
assert len(DATA) == 96_000_000
assert META["target"] in META["probe_map"]["D0"]
assert META["target"] in META["probe_map"]["D2"]
assert "WROOM" in META["probe_map"]["D5"]
assert "WROOM" in META["probe_map"]["D7"]


def edges(bit):
    signal = ((DATA >> bit) & 1).astype(np.int8)
    delta = np.diff(signal)
    return np.flatnonzero(delta == 1) + 1, np.flatnonzero(delta == -1) + 1


def payload(rises, bit, offset):
    values = (DATA[rises + offset] >> bit) & 1
    return [
        f"{sum(int(v) << (7-i) for i, v in enumerate(values[s:s+8])):02X}"
        for s in READ_STARTS
    ]


def review_side(clock_bit, data_bit):
    rises, falls = edges(clock_bit)
    frames = np.split(rises, np.flatnonzero(np.diff(rises) > RATE // 1000) + 1)
    assert len(frames) == len(READINGS) == 5
    assert all(len(frame) == 45 for frame in frames)
    counts = {str(offset): 0 for offset in OFFSETS}
    held_wrong = []
    pulse_widths = []
    bad_exact = 0
    frame_reports = []
    for frame_index, frame in enumerate(frames):
        tx = READINGS[frame_index]["tx"]
        assert [entry["index"] for entry in tx] == list(range(13))
        for tx_index, clock_index in enumerate(TX_CLOCKS):
            expected = tx[tx_index]["desired"]
            assert expected == (1 if clock_index in (7, 44) else 0)
            rise = int(frame[clock_index])
            values = [int((DATA[rise + offset] >> data_bit) & 1) for offset in OFFSETS]
            for offset, value in zip(OFFSETS, values):
                counts[str(offset)] += int(value == expected)
            bad_exact += int(values[2] != expected)
            narrow = ((DATA[rise-24:rise+25] >> data_bit) & 1) != expected
            transitions = np.diff(np.r_[False, narrow, False].astype(np.int8))
            starts = np.flatnonzero(transitions == 1)
            ends = np.flatnonzero(transitions == -1)
            pulse_widths.extend((ends - starts).tolist())
            wide = ((DATA[rise-120:rise+121] >> data_bit) & 1) != expected
            if bool(np.all(wide)):
                held_wrong.append({
                    "frame": frame_index + 1,
                    "tx_index": tx_index,
                    "clock_number": clock_index + 1,
                    "expected_data": expected,
                    "observed_data": values,
                    "wrong_throughout_pm5us": True,
                    "source_trace": tx[tx_index],
                })
        frame_reports.append({
            "frame": frame_index + 1,
            "clock_count": len(frame),
            "cpu_reply": READINGS[frame_index]["raw"].split(),
            "replies_by_offset": {
                str(offset): payload(frame, data_bit, offset) for offset in OFFSETS
            },
        })
    result = {
        "clock_rises": len(rises),
        "clock_falls": len(falls),
        "correct_transmit_bits_by_offset": counts,
        "transmit_bits_checked": 65,
        "wrong_at_exact_clock_rise": bad_exact,
        "wrong_runs_in_pm1us_widths_ns": sorted({round(v * 1e9 / RATE, 3) for v in pulse_widths}),
        "pm1us_duration_limit": "A run filling the whole window is censored; 2041.667 ns is a lower bound, not its full duration.",
        "held_wrong_pm5us": held_wrong,
        "held_wrong_direction_counts": {
            "commanded_0_observed_1": sum(entry["expected_data"] == 0 for entry in held_wrong),
            "commanded_1_observed_0": sum(entry["expected_data"] == 1 for entry in held_wrong),
        },
        "frames": frame_reports,
    }
    return result, rises, falls


source, source_rises, source_falls = review_side(5, 7)
board, board_rises, board_falls = review_side(0, 2)
clock_delays = {}
for name, first, second in [
    ("rising", source_rises, board_rises),
    ("falling", source_falls, board_falls),
]:
    delta = second - first
    values, counts = np.unique(delta, return_counts=True)
    clock_delays[name] = {
        "board_minus_source_samples": values.tolist(),
        "counts": counts.tolist(),
    }

activity = {}
for bit in range(8):
    rising, falling = edges(bit)
    activity[f"D{bit}"] = {"rising": len(rising), "falling": len(falling)}
trace = [entry for reading in READINGS for entry in reading["tx"]]
report = {
    "scope": "Independent offline review; no device access or hardware operations.",
    "capture": CAPTURE.name,
    "capture_sha256": hashlib.sha256(DATA).hexdigest(),
    "sample_rate_hz": RATE,
    "sample_period_ns": 1e9 / RATE,
    "operator_confirmed_probe_map": META["probe_map"],
    "channel_activity": activity,
    "tx_index_to_one_based_clock": [clock + 1 for clock in TX_CLOCKS],
    "association": "All five source and board reply arrays are compared with the corresponding CPU READ report in order. TX records are generated only by writeBit(), not by intervening read clocks.",
    "source_local_pad_trace": {
        "samples": len(trace),
        "input_data_matches_requested": sum(((entry["input"] >> 1) & 1) == entry["desired"] for entry in trace),
        "output_latch_matches_requested": sum(((entry["out"] >> 1) & 1) == entry["desired"] for entry in trace),
        "both_outputs_enabled": sum(entry["enable"] == 3 for entry in trace),
        "timing": "Trace samples are taken during CLOCK LOW, immediately before the requested rising edge; they are not simultaneous with every analyzer offset.",
    },
    "clock_threshold_crossing_delays": clock_delays,
    "wroom_red_clock_brown_data": source,
    "target_green_clock_blue_data": board,
    "all_reply_samples_match_cpu": all(
        reply == frame["cpu_reply"]
        for side in (source, board)
        for frame in side["frames"]
        for reply in frame["replies_by_offset"].values()
    ),
    "limits": [
        "Colors identify analyzer probes here; GREEN and BLUE are also the separate interboard ZDI signal wires. RED and BROWN are added analyzer probes, not signal wires.",
        "A source-side correct settled level and a board-side incorrect settled level establish different digital observations across the signal path. They do not determine analog voltage, resistor value, contact quality, driver current, or a defective component.",
        "Sampled short glitches and clock threshold delays are quantized in 41.667 ns bins. The analyzer cannot exclude shorter disturbances or establish exact eZ80 input thresholds.",
        "Correct connector CLOCK counts do not independently prove correct clock waveform at the eZ80 package pin.",
    ],
}
output = ROOT / "independent-four-probe-review.json"
with output.open("x") as stream:
    json.dump(report, stream, indent=2)
    stream.write("\n")
print(json.dumps({
    "report": str(output),
    "source_correct_by_offset": source["correct_transmit_bits_by_offset"],
    "board_correct_by_offset": board["correct_transmit_bits_by_offset"],
    "source_held_wrong": len(source["held_wrong_pm5us"]),
    "board_held_wrong": len(board["held_wrong_pm5us"]),
    "board_mismatch_directions": board["held_wrong_direction_counts"],
    "all_reply_samples_match_cpu": report["all_reply_samples_match_cpu"],
}, indent=2))
