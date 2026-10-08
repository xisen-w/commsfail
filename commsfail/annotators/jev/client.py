"""Audited Decisions API calls; no chat endpoint, model fallback, or secret in artifacts."""
from __future__ import annotations
import hashlib
import json
import math
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from . import MODEL

ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
MAX_BYTES = 30000  # Conservative UTF-8 byte bound, below the advertised 32K-token context.


def encoded(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def digest(obj):
    return hashlib.sha256(encoded(obj)).hexdigest()


def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        os.chmod(tmp, 0o600)
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")
    tmp.replace(path)


def read(path):
    return json.loads(Path(path).read_text())


def probability(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and 0 <= value <= 1


def validate_response(obj, questions):
    model = obj.get("model", "")
    if model != MODEL and not model.startswith(MODEL + "-"):
        raise ValueError("serving model mismatch")
    if obj.get("provider") != "TypeSafe":
        raise ValueError("serving provider mismatch")
    if not isinstance(obj.get("id"), str) or not obj["id"]:
        raise ValueError("missing request id")
    answers = obj.get("answers")
    if not isinstance(answers, dict) or set(answers) != set(questions):
        raise ValueError("missing or unexpected answers")
    for key, question in questions.items():
        answer = answers[key]
        if not isinstance(answer, dict) or answer.get("type") != question["type"]:
            raise ValueError("answer type mismatch: " + key)
        if question["type"] == "noul":
            if not probability(answer.get("noul")):
                raise ValueError("invalid probability: " + key)
        elif question["type"] == "choice":
            options = question["criteria"]
            probs = answer.get("probabilities", {})
            if (answer.get("choice") not in options or set(probs) != set(options)
                    or not all(probability(p) for p in probs.values())
                    or abs(sum(probs.values()) - 1) > .03
                    or not probability(answer.get("confidence"))):
                raise ValueError("invalid choice distribution: " + key)
        else:
            raise ValueError("unsupported primitive")
    usage = obj.get("usage", {})
    for key in ("input_tokens", "output_tokens", "cost"):
        value = usage.get(key)
        if value is not None and (not isinstance(value, (int, float)) or isinstance(value, bool)
                                  or not math.isfinite(value) or value < 0):
            raise ValueError("invalid usage")
    return answers


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Decisions:
    def __init__(self, root, key_file=None, retries=3, transport=None, sleep=time.sleep):
        self.root, self.retries = Path(root), retries
        self.transport, self.sleep = transport, sleep
        self.key = (os.environ.get("OPENROUTER_API_KEY") or
                    (Path(key_file).read_text().strip() if key_file else ""))
        if not self.key and transport is None:
            raise ValueError("OPENROUTER_API_KEY or --key-file is required")

    def call(self, state, questions, tag):
        body = dict(model=MODEL, state=state, questions=questions)
        payload = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()
        if len(payload) > MAX_BYTES:
            raise ValueError(f"request exceeds {MAX_BYTES} bytes; no silent truncation")
        if self.key and self.key.encode() in payload:
            raise ValueError("credential detected in request state")
        folder = self.root / tag
        folder.mkdir(parents=True, exist_ok=True, mode=0o700)
        reqfile, response = folder / "request.json", folder / "response.json"
        if reqfile.exists() and digest(read(reqfile)) != digest(body):
            raise ValueError("cached request changed; use a new output root")
        write(reqfile, body)
        if response.exists():
            obj = read(response)
            return validate_response(obj, questions)
        existing = list(folder.glob("attempt-*.json"))
        start = len(existing)
        # Each explicit resume gets a new bounded attempt set; old attempts stay intact.
        for k in range(self.retries + 1):
            t0 = time.monotonic()
            path = folder / f"attempt-{start+k:04d}.json"
            try:
                if self.transport:
                    obj = self.transport(body)
                else:
                    req = urllib.request.Request(ENDPOINT, data=payload, headers={
                        "Authorization": "Bearer " + self.key, "Content-Type": "application/json",
                        "X-Title": "commsfail-jev-annotation"})
                    with urllib.request.build_opener(NoRedirect).open(req, timeout=90) as res:
                        obj = json.load(res)
                write(path, {"response": obj, "seconds": round(time.monotonic()-t0, 3)})
                answer = validate_response(obj, questions)
                write(response, obj)
                return answer
            except urllib.error.HTTPError as exc:
                # Do not persist remote error bodies or request headers.
                write(path, {"http_status": exc.code, "seconds": round(time.monotonic()-t0, 3)})
                if exc.code not in (408, 429, 500, 502, 503, 504, 524, 529) or k == self.retries:
                    raise RuntimeError(f"Decisions API HTTP {exc.code}") from None
                try:
                    delay = min(60., max(1., float(exc.headers.get("Retry-After", 2**k))))
                except (ValueError, AttributeError):
                    delay = 2**k
                self.sleep(delay)
            except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
                write(path, {"error_type": type(exc).__name__, "seconds": round(time.monotonic()-t0, 3)})
                if k == self.retries:
                    raise RuntimeError("Decisions API transport failure") from None
                self.sleep(min(30, 2**k))
        raise RuntimeError("request exhausted")


def usage(root):
    rows = [read(p) for p in Path(root).rglob("response.json")]
    billed = [read(p).get("response") for p in Path(root).rglob("attempt-*.json")]
    billed = {o["id"]: o for o in billed if isinstance(o, dict) and o.get("id")}
    costs = [o.get("usage", {}).get("cost") for o in billed.values()]
    return {"validated_requests": len(rows), "responses_received": len(billed),
            "served_models": sorted({o["model"] for o in rows}),
            "known_cost_usd": sum(c for c in costs if c is not None),
            "cost_complete": all(c is not None for c in costs),
            "input_tokens": sum(o.get("usage", {}).get("input_tokens", 0) for o in billed.values()),
            "failed_attempts": sum("response" not in read(p) for p in Path(root).rglob("attempt-*.json"))}
