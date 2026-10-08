"""Run with python -m commsfail.annotators.jev; the standard CLI is unchanged."""
from __future__ import annotations
import argparse
import fcntl
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from . import MODEL, VERSION
from .client import Decisions, digest, read, write, usage
from .evidence import source_manifest
from .pipeline import annotate, choice, protocol_id, validate_completed


def run_batch(src, out, pattern="research__*__n[234]__r1", workers=2, key_file=None, retries=3):
    src, out = Path(src).resolve(), Path(out).resolve()
    if workers < 1 or retries < 0 or "/" in pattern or pattern in (".", ".."):
        raise ValueError("invalid workers, retries, or direct-child pattern")
    if src == out or src in out.parents or out in src.parents:
        raise ValueError("input and output roots must be separate")
    runs = sorted(p for p in src.glob(pattern) if p.is_dir())
    if not runs:
        raise ValueError("no source records matched")
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (out / ".lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("another batch owns this output root") from None
        config = dict(source=str(src), pattern=pattern, runs=[p.name for p in runs], model=MODEL,
                      version=VERSION, protocol=protocol_id(), workers=workers, retries=retries,
                      inputs={p.name: digest(source_manifest(p)) for p in runs})
        if (out / "config.json").exists() and read(out / "config.json") != config:
            raise ValueError("batch configuration/input changed; choose a fresh output root")
        write(out / "config.json", config)
        summary = dict(selected=len(runs), completed=0, failed=0, pending=len(runs), records=[])
        write(out / "summary.json", summary)
        def one(p):
            dest = out / p.name
            try:
                if (dest / "COMPLETE.json").exists() and not validate_completed(dest, p.name, check_hashes=True):
                    return {"run": p.name, "status": "skipped", "usage": read(dest / "annotation.json")["usage"]}
                rec = annotate(p, dest, key_file=key_file, retries=retries)
                return {"run": p.name, "status": "completed", "usage": rec["usage"]}
            except Exception as exc:
                # Local error classes/messages only; the HTTP layer suppresses remote error bodies.
                error = {"run": p.name, "status": "failed", "error": str(exc)}
                write(out / "logs" / (p.name + ".json"), error)
                return error
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for future in as_completed([pool.submit(one, p) for p in runs]):
                row = future.result()
                summary["records"].append(row)
                summary["records"].sort(key=lambda r: r["run"])
                summary["failed" if row["status"] == "failed" else "completed"] += 1
                summary["pending"] -= 1
                summary["usage"] = usage(out)
                write(out / "summary.json", summary)
                print(json.dumps({k: summary[k] for k in ("selected", "completed", "failed", "pending")}), flush=True)
        return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    batch = sub.add_parser("annotate-batch")
    batch.add_argument("records")
    batch.add_argument("--out", required=True)
    batch.add_argument("--pattern", default="research__*__n[234]__r1")
    batch.add_argument("--workers", type=int, default=2)
    batch.add_argument("--retries", type=int, default=3)
    batch.add_argument("--key-file")
    check = sub.add_parser("validate")
    check.add_argument("output")
    smoke = sub.add_parser("smoke")
    smoke.add_argument("--out", required=True)
    smoke.add_argument("--key-file")
    args = parser.parse_args(argv)
    os.umask(0o077)
    try:
        if args.command == "annotate-batch":
            return int(bool(run_batch(args.records, args.out, args.pattern, args.workers, args.key_file, args.retries)["failed"]))
        if args.command == "validate":
            cfg = read(Path(args.output) / "config.json")
            errors = {run: validate_completed(Path(args.output) / run, run, True) for run in cfg["runs"]}
            print(json.dumps(errors, indent=2))
            return int(any(errors.values()))
        client = Decisions(Path(args.out) / "requests", key_file=args.key_file)
        answers = client.call({"text": "A reports that tests passed. The command log shows exit code 1 and failed tests."}, {
            "contradicted": choice("Does the log contradict the claim that tests passed?", {
                "yes": "The trace explicitly shows failed tests.", "no": "The trace explicitly shows passing tests.",
                "unknown": "The trace is insufficient."})}, "synthetic-positive")
        negative = client.call({"text": "A reports that tests passed. The command log shows exit code 0 and all tests passed."}, {
            "contradicted": choice("Does the log contradict the claim that tests passed?", {
                "yes": "The trace explicitly shows failed tests.", "no": "The trace explicitly shows passing tests.",
                "unknown": "The trace is insufficient."})}, "synthetic-negative")
        report = {"positive": answers, "negative": negative, "usage": usage(Path(args.out) / "requests"),
                  "passed": answers["contradicted"]["choice"] == "yes" and negative["contradicted"]["choice"] == "no"}
        write(Path(args.out) / "smoke.json", report)
        print(json.dumps(report))
        return int(not report["passed"])
    except (OSError, ValueError, RuntimeError) as exc:
        print(type(exc).__name__ + ": " + str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
