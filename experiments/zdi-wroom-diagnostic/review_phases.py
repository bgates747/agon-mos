"""Offline four-probe review. Reads archives; creates only a new JSON report."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import numpy as np
import sys

ROOT = Path(sys.argv[1]).resolve(strict=True)
META = json.loads((ROOT / "result.json").read_text())
RATE = 24_000_000
OFFSETS = [-120, -24, 0, 24, 120]
TX_CLOCKS = list(range(9)) + [17, 26, 35, 44]
READ_STARTS = [9, 18, 27, 36]

def hist(values):
    return {str(int(k)): int(v) for k, v in sorted(Counter(map(int, values)).items())}

def summary(values):
    a = np.asarray(values)
    return {"minimum": float(np.min(a)), "median": float(np.median(a)),
            "maximum": float(np.max(a)), "samples": len(a)} if len(a) else None

def edge_info(data, bit):
    delta = np.diff(((data >> bit) & 1).astype(np.int8))
    rises = np.flatnonzero(delta == 1) + 1
    falls = np.flatnonzero(delta == -1) + 1
    # Retain all raw edges. Collapse only for explicit nominal-clock indexing.
    clusters = np.split(rises, np.flatnonzero(np.diff(rises) >= 120) + 1)
    stable = np.array([c[-1] for c in clusters])
    frames = np.split(stable, np.flatnonzero(np.diff(stable) > 24000) + 1)
    next_fall = np.searchsorted(falls, rises)
    usable = next_fall < len(falls)
    high_width = falls[next_fall[usable]] - rises[usable]
    low_width = rises - falls[next_fall - 1]
    # Long idle HIGH gaps between requests are excluded from timing summaries.
    within = high_width < 24000
    periods = np.concatenate([np.diff(frame) for frame in frames])
    return {"rises": rises, "falls": falls, "stable": stable, "frames": frames,
        "report": {"raw_rising_edges": len(rises), "raw_falling_edges": len(falls),
            "expected_raw_rises_for_five_reads": 225,
            "raw_rise_delta_from_expected": len(rises) - 225,
            "nominal_stable_rises": len(stable), "nominal_frame_lengths": list(map(len, frames)),
            "extra_rises": len(rises) - len(stable),
            "short_high_pulses": [{"rise_sample": int(r), "width_samples": int(w)}
                for r, w in zip(rises[usable], high_width) if w < 120],
            "short_low_pulse_widths_samples": hist(low_width[low_width < 120]),
            "within_request_high_duration_us": summary(high_width[within] / 24),
            "nominal_low_duration_us": summary(low_width[low_width >= 120] / 24),
            "nominal_rise_period_us": summary(periods / 24),
            "nominal_rise_frequency_hz": summary(RATE / periods),
            "first_to_stable_rise_delay_samples": hist([c[-1] - c[0] for c in clusters])}}

def payload(data, frame, bit, offset):
    values = (data[frame + offset] >> bit) & 1
    return [f"{sum(int(v) << (7-i) for i, v in enumerate(values[s:s+8])):02X}"
            for s in READ_STARTS]

def side_review(data, clock, bit, readings):
    frames = clock["frames"]
    assert len(frames) == len(readings) == 5
    assert all(len(frame) == 45 for frame in frames)
    correct = {str(offset): 0 for offset in OFFSETS}
    held = []
    wrong_runs = []
    frame_reports = []
    for fi, (frame, reading) in enumerate(zip(frames, readings)):
        traces = reading["tx"]
        assert [t["index"] for t in traces] == list(range(13))
        for ti, ci in enumerate(TX_CLOCKS):
            expected = traces[ti]["desired"]
            assert expected == int(ci in (7, 44))
            rise = int(frame[ci])
            values = [int((data[rise + off] >> bit) & 1) for off in OFFSETS]
            for off, val in zip(OFFSETS, values):
                correct[str(off)] += int(val == expected)
            wrong = ((data[rise-24:rise+25] >> bit) & 1) != expected
            delta = np.diff(np.r_[False, wrong, False].astype(np.int8))
            wrong_runs.extend((np.flatnonzero(delta == -1) - np.flatnonzero(delta == 1)).tolist())
            wide = ((data[rise-120:rise+121] >> bit) & 1) != expected
            if np.all(wide):
                held.append({"frame": fi+1, "tx_index": ti, "clock_number": ci+1,
                    "rise_sample": rise, "expected": expected, "observed": 1-expected})
        frame_reports.append({"frame": fi+1, "cpu_reply": reading["raw"].split(),
            "reply_by_offset": {str(off): payload(data, frame, bit, off) for off in OFFSETS}})
    return {"transmit_bits_checked": 65, "correct_transmit_bits_by_offset": correct,
        "held_wrong_throughout_pm5us_count": len(held), "held_wrong_events": held,
        "held_wrong_direction_counts": {
            "commanded_0_observed_1": sum(e["expected"] == 0 for e in held),
            "commanded_1_observed_0": sum(e["expected"] == 1 for e in held)},
        "wrong_runs_in_pm1us_widths_ns": {str(round(int(k)*1e9/RATE, 3)): v
                                            for k,v in hist(wrong_runs).items()},
        "all_reply_offsets_match_cpu": all(f["cpu_reply"] == reply
            for f in frame_reports for reply in f["reply_by_offset"].values()),
        "frames": frame_reports}

phases = []
for phase in META["phases"]:
    path = ROOT / (phase["id"] + ".bin")
    data = np.memmap(path, dtype=np.uint8, mode="r")
    assert len(data) == 96_000_000
    source_clock = edge_info(data, 5)
    board_clock = edge_info(data, 0)
    if (len(source_clock['frames']) != 5 or len(board_clock['frames']) != 5
            or any(len(f) != 45 for f in source_clock['frames'])
            or any(len(f) != 45 for f in board_clock['frames'])):
        result = dict(capture=path.name, sha256=hashlib.sha256(data).hexdigest(),
                      clock_mode=phase['clock_mode'],
                      clock_drive_level=phase.get('clock_drive_level'),
                      valid_cpu_ids=phase['valid_count'], nominal_mapping_valid=False,
                      clock_wroom_red_D5=source_clock['report'],
                      clock_target_green_D0=board_clock['report'],
                      reason='Unexpected nominal clock counts: do not force TX/reply indexing')
        phases.append(result)
        print(json.dumps(result))
        continue
    source = side_review(data, source_clock, 7, phase["readings"])
    board = side_review(data, board_clock, 2, phase["readings"])
    delays = {}
    for key in ("rises", "falls", "stable"):
        assert len(source_clock[key]) == len(board_clock[key])
        delays[key + "_board_minus_source_samples"] = hist(board_clock[key] - source_clock[key])
    trace = [t for r in phase["readings"] for t in r["tx"]]
    result = {"capture": path.name, "sha256": hashlib.sha256(data).hexdigest(),
        "nominal_mapping_valid": True,
        "clock_mode": phase["clock_mode"], "clock_drive_level": phase.get("clock_drive_level"), "valid_cpu_ids": phase["valid_count"],
        "source_local_trace": {"samples": len(trace),
            "input_matches_desired": sum(((t["input"] >> 1) & 1) == t["desired"] for t in trace),
            "output_latch_matches_desired": sum(((t["out"] >> 1) & 1) == t["desired"] for t in trace),
            "outputs_enabled": sum(t["enable"] == 3 for t in trace)},
        "clock_wroom_red_D5": source_clock["report"],
        "clock_target_green_D0": board_clock["report"],
        "clock_end_threshold_delays": delays,
        "data_wroom_brown_D7": source, "data_target_blue_D2": board}
    phases.append(result)
    print(json.dumps({"capture": path.name, "mode": phase["clock_mode"],
        "extra_clock_rises": source_clock["report"]["extra_rises"],
        "source_correct": source["correct_transmit_bits_by_offset"],
        "board_correct": board["correct_transmit_bits_by_offset"],
        "source_held_wrong": source["held_wrong_throughout_pm5us_count"],
        "board_held_wrong": board["held_wrong_throughout_pm5us_count"],
        "all_reply_match": source["all_reply_offsets_match_cpu"] and board["all_reply_offsets_match_cpu"]}))

report = {"scope": "Offline four-probe phase comparison. No device operations.",
    "sample_rate_hz": RATE, "sample_period_ns": 1e9/RATE,
    "probe_map": META["probe_map"], "phase_order": [dict(mode=p["clock_mode"], drive=p.get("clock_drive_level")) for p in META["phases"]],
    "offset_samples_and_microseconds": {str(off): off/24 for off in OFFSETS},
    "tx_index_to_one_based_clock": [c+1 for c in TX_CLOCKS],
    "mapping_method": "For nominal indexing only, rising edges less than5us apart are grouped and the final rise is selected. Every raw extra edge remains reported. Each side then has5frames of45nominal rises, ordered against the5CPU replies and65TX trace samples.",
    "phases": phases,
    "limits": [
        "Open-drain clock is slower at the rising threshold; DATA sampled before its final rising crossing is not the same temporal reference as push-pull. Positive1us and5us offsets are separately retained.",
        "Raw CLOCK chatter may be recognized by the target even though nominal decoding removes it for comparison. Successful nominal decoding does not prove correct target framing.",
        "A41.667ns reported pulse occupies one analyzer sample; shorter disturbances and analog edge shape are unresolved.",
        "A wrong run filling the full plus/minus1us window is censored at2041.667ns; it is not a measured total pulse duration.",
        "GPIO source input trace is sampled with CLOCK low before the rising edge. Output latch, physical input, and enable are distinct registers.",
        "Digital differences across resistor ends do not identify resistance, analog voltage, contact quality, driver current, or a damaged component.",
        "Phase order reverses twice without target resets; this is an order-control comparison, not randomization or target-state elimination."]}
output = ROOT / "four-probe-phase-review.json"
with output.open("x") as stream:
    json.dump(report, stream, indent=2)
    stream.write("\n")
print(str(output))
