"""A/B pattern decisions, typed adjudication, then outcome-visible grade attribution."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from ..taxonomy import load_choice
from ..standard.bundle import QUESTIONS, SEVERITY
from . import MODEL, SCHEMA, VERSION
from .client import Decisions, digest, read, write, usage
from .evidence import Evidence, clean, source_manifest

CLASSES = tuple(c for c, _ in QUESTIONS)
TAXONOMY = load_choice("state_gap")
PATTERNS = {p["id"]: p for p in TAXONOMY["modes"] if p["group"] in CLASSES}
GROUPS = {g["id"]: g for g in TAXONOMY["groups"] if g["id"] in CLASSES}
EMPTY = {"none", "undecidable"}
CAUSES = {
    "incident": "A retained communication incident causally contributed to the lost points; not mere co-occurrence.",
    "capability": "The agreed work was carried out but technically weak or wrong.",
    "collective_judgement": "The agents shared and implemented a poor decision.",
    "task_data": "The supplied task or data could not support the rubric item.",
    "harness": "The experiment runner or execution environment caused the loss.",
    "grader": "The recorded grade conflicts with the deliverable evidence.",
    "undecidable": "Evidence does not distinguish a primary cause."}


def choice(instructions, criteria):
    return {"type": "choice", "instructions": instructions, "criteria": criteria}


def protocol_id():
    root = Path(__file__).parent
    files = list(root.glob("*.py")) + list(root.glob("*.json")) + [root / "PROTOCOL.md"]
    files += list((root.parent / "standard").glob("*.py"))
    files += list((root.parent / "taxonomy-choices").glob("*.json"))
    return digest({str(p.relative_to(root.parent)): p.read_text() for p in sorted(files)})


def questions(state, reverse=False, judge=False):
    result = {}
    for cls in CLASSES:
        opts = {p["id"]: p["definition"] for p in PATTERNS.values() if p["group"] == cls}
        opts.update(none="No incident of this class first breaks at the focal post. "
                    "Ordinary overhead, technical weakness and collective bad decisions are not communication failures.",
                    undecidable="The selected evidence cannot establish or rule out this class at the focal post.")
        if reverse:
            opts = dict(reversed(list(opts.items())))
        rule = (f"Choose the best supported pattern of {cls} anchored at focal_post.seq. "
                f"Definition: {GROUPS[cls]['definition']} Evidence needed: {GROUPS[cls]['evidence']}. "
                "The anchor is the first broken step, not every later mention. Keep repaired failures. "
                "Apply state.class_order IN ORDER to each incident; use the FIRST failed link only. "
                "Different classes may be selected only for distinct incidents. At most one pattern per class at this post. "
                "Do not infer a failure merely from missing excerpts. Prefer undecidable when relevant evidence is omitted.")
        if cls == "unsaid":
            rule += " Require an explicit agent action and complete board coverage to infer undisclosed information."
            if not state["coverage"]["timeline_complete"]:
                opts = {"undecidable": "The full board is not present; nondisclosure cannot be checked.",
                        "none": "Positive evidence establishes disclosure or that no disclosure was needed."}
        if judge:
            rule += " Independently adjudicate the A/B decisions in state; they may both be wrong. You may add a missed pattern."
        result[cls] = choice(rule, opts)
    return result


def labels(answers):
    return {k: a["choice"] for k, a in answers.items()}


def agreement(a, b):
    """Fixed post/class slots, not the standard pipeline's span matching metric."""
    per_class = {}
    for cls in CLASSES:
        pairs = [(a[k][cls]["choice"], b[k][cls]["choice"]) for k in sorted(a)]
        n = len(pairs)
        same = sum(x == y for x, y in pairs)
        n_a = sum(x not in EMPTY for x, _ in pairs)
        n_b = sum(y not in EMPTY for _, y in pairs)
        both = sum(x not in EMPTY and y not in EMPTY for x, y in pairs)
        # Unknowns remain explicit and are excluded from binary kappa.
        decided = [(x not in EMPTY, y not in EMPTY) for x, y in pairs if "undecidable" not in (x, y)]
        kappa = None
        if decided:
            pa = sum(x for x, _ in decided) / len(decided)
            pb = sum(y for _, y in decided) / len(decided)
            pe = pa * pb + (1-pa) * (1-pb)
            po = sum(x == y for x, y in decided) / len(decided)
            if pe < 1:
                kappa = (po-pe)/(1-pe)
        per_class[cls] = dict(slots=n, exact_label_matches=same, positive_A=n_a, positive_B=n_b,
                              both_positive=both, decided_pairs=len(decided), binary_kappa=kappa)
    return {"unit": "post/class slot", "same_model_repeats": True,
            "independent_model_validation": False, "classes": per_class}


def detail_questions(pattern, state, index, seq):
    q = "For the proposed incident " + pattern + ": "
    refs = {b["id"]: b["ref"] + " (content is in state.evidence)" for b in state["evidence"]}
    refs["undecidable"] = "No selected block supports this claim."
    out = {
        "supported": choice(q + "Does the selected evidence establish an incident, anchored at the focal post?", {
            "yes": "Concrete evidence supports the pattern and anchor.",
            "no": "Evidence contradicts this incident or places its first break elsewhere.",
            "undecidable": "Missing evidence or ambiguous anchor prevents a decision."}),
        "severity": choice(q + "What happened to the work? Use observed consequences, not hypothetical risk.", {
            **{str(n): name + ": " + desc for n, name, desc in SEVERITY},
            "undecidable": "Consequences cannot be established from these excerpts."}),
        "repaired": choice(q + "Was the gap repaired within this run?", {
            "yes": "A later action visibly resolves the gap.", "no": "It remains unresolved at the end.",
            "undecidable": "The resolution cannot be established."}),
        "source": choice(q + "Who caused the gap?", {
            "agents": "Agent communication or actions caused it.", "harness": "The runner caused it.",
            "undecidable": "The evidence cannot distinguish agent from runner causation."}),
        "evidence": choice(q + "Select the primary evidence block supporting the failure, not background context.", refs)}
    cls = PATTERNS[pattern]["group"]
    if cls == "unreceived":
        focal = index["posts"][str(seq)]
        seen = focal.get("seen")
        candidates = {s: f"Post P{s} by {p['who']}, not received at the focal action."
                      for s, p in index["posts"].items() if seen is not None and seen < int(s) < seq
                      and p["who"] != focal["who"]}
        # Only offer posts whose text actually appears in the selected excerpts.
        import re
        evidence_text = "\n".join(b["text"] for b in state["evidence"])
        candidates = {s: v for s, v in candidates.items() if re.search(rf"\bP{s}\b", evidence_text)}
        candidates["undecidable"] = "No evidenced unseen earlier post can be identified."
        out["unseen_post"] = choice(q + "Which unreceived post was needed when the focal agent acted?", candidates)
    return out


def validate_grade(grade):
    import math
    items = grade.get("items")
    if not isinstance(items, list):
        raise ValueError("grade requires an items array; scalar scores are unsupported")
    seen = set()
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("index"), int) or item["index"] in seen:
            raise ValueError("rubric indices must be unique integers")
        seen.add(item["index"])
        for field in ("score", "weight"):
            value = item.get(field)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value < 0:
                raise ValueError("invalid rubric " + field)
        if item["score"] > 100:
            raise ValueError("rubric score exceeds 100")
    return items


def annotate(src, out, key_file=None, retries=3, transport=None):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    fingerprint = source_manifest(src)
    config = {"version": VERSION, "model": MODEL, "protocol": protocol_id(),
              "source": str(Path(src).resolve()), "input_hash": digest(fingerprint), "retries": retries}
    if (out / "config.json").exists() and read(out / "config.json") != config:
        raise ValueError("run configuration or input changed; choose a new output directory")
    write(out / "config.json", config)
    write(out / "input-manifest.json", fingerprint)
    # Preflight validates shape, but grade contents are not passed to blind stages.
    validate_grade(read(Path(src) / "score.json"))
    ev = Evidence(src, out / "bundle")
    ev.write_manifest()
    client = Decisions(out / "requests", key_file=key_file, retries=retries, transport=transport)
    contexts = {str(p["seq"]): ev.state(p) for p in ev.agent_posts}
    def pass_one(tag):
        return {seq: client.call(state, questions(state, reverse=tag == "B"), f"{tag}/P{seq}")
                for seq, state in contexts.items()}
    with ThreadPoolExecutor(max_workers=2) as pool:
        fa, fb = pool.submit(pass_one, "A"), pool.submit(pass_one, "B")
        a, b = fa.result(), fb.result()
    write(out / "A.json", a)
    write(out / "B.json", b)
    write(out / "agreement.json", agreement(a, b))
    incidents, uncertain, rejected, sweep, judged = [], [], [], [], {}
    for seq, state in contexts.items():
        judge_state = {**state, "annotator_A": labels(a[seq]), "annotator_B": labels(b[seq])}
        answers = client.call(judge_state, questions(state, judge=True), f"judge/P{seq}")
        judged[seq] = answers
        kept = []
        for cls, ans in answers.items():
            pattern = ans["choice"]
            if pattern == "undecidable":
                uncertain.append({"post": int(seq), "class": cls, "stage": "judge", "reason": "insufficient evidence"})
            if pattern in EMPTY:
                continue
            detail = client.call({**state, "proposed_pattern": pattern},
                                 detail_questions(pattern, state, ev.index, int(seq)), f"detail/P{seq}/{cls}")
            values = labels(detail)
            block = ev.by_id.get(values["evidence"])
            valid = values["supported"] == "yes" and block is not None
            if cls == "unreceived" and values.get("unseen_post") == "undecidable":
                valid = False
            if cls == "unsaid" and (not state["coverage"]["timeline_complete"] or not block
                                      or not block["ref"].startswith("agents/")):
                valid = False
            if not valid:
                rejected.append({"post": int(seq), "class": cls, "pattern": pattern,
                                 "stage": "evidence", "decisions": values})
                uncertain.append({"post": int(seq), "class": cls, "stage": "evidence", "reason": "candidate not established"})
                continue
            inc = {"id": f"P{seq}:{cls}", "anchor": int(seq), "class": cls, "pattern": pattern,
                   "evidence_ref": block["ref"], "evidence_block_id": block["id"],
                   "severity": int(values["severity"]) if values["severity"].isdigit() else None,
                   "repaired": {"yes": True, "no": False}.get(values["repaired"]),
                   "source": values["source"], "probabilities": ans["probabilities"],
                   "details": detail, "coverage": state["coverage"], "explanation": None}
            if cls == "unreceived":
                inc["unseen_post"] = int(values["unseen_post"])
            incidents.append(inc)
            kept.append(inc["id"])
        sweep.append({"post": int(seq), "incidents": kept, "decisions": labels(answers), "coverage": state["coverage"]})
    final = {"incidents": incidents, "uncertain": uncertain, "rejected": rejected, "sweep": sweep}
    write(out / "judge.json", judged)
    write(out / "final.json", final)  # Freeze blind annotations before exposing any grade to a model.
    final_hash = digest(final)
    grade = clean(read(Path(src) / "score.json"))
    rubric = validate_grade(grade)
    verdict_items = []
    compact = [{k: inc[k] for k in ("id", "anchor", "class", "pattern", "evidence_ref", "severity")} for inc in incidents]
    for item in rubric:
        if item["score"] == 100:
            continue
        idx = item["index"]
        state = ev.state(query=str(item.get("content", "")) + " " + str(item.get("reasoning", "")),
                         extra={"rubric_item": item, "final_incidents": compact})
        options = {i["id"]: f"{i['pattern']} at P{i['anchor']}" for i in incidents}
        options["none"] = "No retained incident is supported as a cause."
        ans = client.call(state, {
            "cause": choice("What primary cause best explains this rubric item's lost points? "
                            "Use trace evidence as well as grader reasoning. Correlation is insufficient.", CAUSES),
            "incident": choice("Which retained incident is the primary causal contributor, if any?", options)},
                            f"verdict/item-{idx}")
        cause, inc = ans["cause"]["choice"], ans["incident"]["choice"]
        if cause == "incident" and inc == "none":
            cause = "undecidable"
        verdict_items.append({"index": idx, "score": item["score"], "weight": item["weight"],
                              "primary_cause": cause, "incident": inc if cause == "incident" else None,
                              "decisions": ans, "coverage": state["coverage"], "explanation": None})
    verdict = {"schema": "commsfail/jev-verdict.v1", "items": verdict_items,
               "final_sha256": final_hash, "method": "typed primary-cause attribution; no generated rationale"}
    write(out / "verdict.json", verdict)
    if digest(read(out / "final.json")) != final_hash or source_manifest(src) != fingerprint:
        raise ValueError("blind final record or input changed during annotation")
    # Every A/B positive slot is accounted for without inventing a judge rationale.
    accounting = []
    kept_labels = {(i["anchor"], i["class"]): i["pattern"] for i in incidents}
    for tag, decisions in (("A", a), ("B", b)):
        for seq, values in decisions.items():
            for cls, answer in values.items():
                if answer["choice"] not in EMPTY:
                    accounting.append({"from": f"{tag}:P{seq}:{cls}", "pattern": answer["choice"],
                                       "disposition": "kept" if kept_labels.get((int(seq), cls)) == answer["choice"] else "not_retained"})
    record = {"schema": SCHEMA, "version": VERSION, "run": Path(src).name, "model": MODEL,
              "protocol": config["protocol"], "evidence_level": "E3", **final,
              "accounting": accounting, "agreement": read(out / "agreement.json"),
              "verdict": verdict, "usage": usage(out / "requests"),
              "limitations": ["bounded evidence retrieval", "at most one pattern per class per focal post",
                              "post anchors are not merged into cross-post incidents", "A/B use the same model",
                              "no generated causal explanations", "automated decisions are not a human gold standard"]}
    write(out / "annotation.json", record)
    errors = validate_completed(out, Path(src).name)
    if errors:
        raise ValueError("; ".join(errors))
    artifacts = {str(p.relative_to(out)): __import__("hashlib").sha256(p.read_bytes()).hexdigest()
                 for p in out.rglob("*.json") if p.name != "COMPLETE.json"}
    write(out / "COMPLETE.json", {"artifacts": artifacts, "config_hash": digest(config)})
    return record


def validate_completed(out, run, check_hashes=False):
    out = Path(out)
    try:
        rec, final, verdict, cfg, index = (read(out / p) for p in
            ("annotation.json", "final.json", "verdict.json", "config.json", "bundle/index.json"))
        errs = []
        from jsonschema import Draft202012Validator
        schema = read(Path(__file__).with_name("schema.json"))
        errs += ["schema: " + e.message for e in Draft202012Validator(schema).iter_errors(rec)]
        if rec["schema"] != SCHEMA or rec["run"] != run or index["run"] != run or rec["model"] != MODEL:
            errs.append("identity mismatch")
        if rec["protocol"] != cfg["protocol"] or cfg["protocol"] != protocol_id():
            errs.append("protocol mismatch")
        if rec["verdict"] != verdict or verdict["final_sha256"] != digest(final):
            errs.append("verdict/final mismatch")
        for key in ("incidents", "rejected", "uncertain", "sweep"):
            if rec[key] != final[key]:
                errs.append("final mismatch: " + key)
        expected = sorted(int(n) for n, p in index["posts"].items() if p["role"] == "agent")
        if sorted(s["post"] for s in rec["sweep"]) != expected:
            errs.append("incomplete or duplicate sweep")
        ids = set()
        manifest = read(out / "bundle/evidence-manifest.json")
        refs = {b["id"]: b["ref"] for b in manifest["blocks"]}
        for i in rec["incidents"]:
            if i["id"] in ids or i["anchor"] not in expected:
                errs.append("invalid incident id/anchor")
            ids.add(i["id"])
            if PATTERNS.get(i["pattern"], {}).get("group") != i["class"]:
                errs.append("pattern/class mismatch")
            if refs.get(i["evidence_block_id"]) != i["evidence_ref"]:
                errs.append("unknown evidence reference")
            if i["severity"] is not None and (type(i["severity"]) is not int or not 1 <= i["severity"] <= 5):
                errs.append("invalid severity")
            if i["class"] == "unreceived":
                p, s = index["posts"][str(i["anchor"])], i.get("unseen_post")
                other = index["posts"].get(str(s), {})
                if p["seen"] is None or s is None or not p["seen"] < s < i["anchor"] or other.get("who") == p["who"]:
                    errs.append("unreceived without an evidenced unseen post")
        grade = read(Path(cfg["source"]) / "score.json")
        lost = sorted(it["index"] for it in validate_grade(grade) if it["score"] < 100)
        if sorted(it["index"] for it in verdict["items"]) != lost:
            errs.append("verdict does not cover every lost rubric item")
        for item in verdict["items"]:
            if item["primary_cause"] not in CAUSES or (item["primary_cause"] == "incident" and item["incident"] not in ids):
                errs.append("invalid verdict cause/reference")
        a, b = read(out / "A.json"), read(out / "B.json")
        if rec["agreement"] != agreement(a, b) or read(out / "agreement.json") != rec["agreement"]:
            errs.append("agreement mismatch")
        from .client import validate_response
        for response in (out / "requests").rglob("response.json"):
            validate_response(read(response), read(response.with_name("request.json"))["questions"])
        if check_hashes:
            import hashlib
            complete = read(out / "COMPLETE.json")
            if complete["config_hash"] != digest(cfg):
                errs.append("completion config mismatch")
            for name, checksum in complete["artifacts"].items():
                if hashlib.sha256((out / name).read_bytes()).hexdigest() != checksum:
                    errs.append("artifact hash mismatch: " + name)
        return errs
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        return ["incomplete or malformed output: " + type(exc).__name__]
