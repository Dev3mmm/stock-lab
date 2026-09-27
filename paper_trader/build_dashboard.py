"""Builds the Stock Lab dashboard (scoreboard + live ST07 paper account) into ../site/index.html"""
import json, os, re, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site")
os.makedirs(SITE, exist_ok=True)


def read_jsonl(p):
    if not os.path.exists(p):
        return []
    out = []
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def parse_scoreboard(path):
    """Pull every markdown table row + verdict into a flat list for the page."""
    rows, header_note = [], ""
    if not os.path.exists(path):
        return rows, header_note
    text = open(path, encoding="utf-8").read()
    lines = text.splitlines()
    header_note = lines[0].lstrip("# ").strip() if lines else ""
    section = ""
    for l in lines:
        if l.startswith("## "):
            section = l[3:].strip()
        if l.startswith("|") and "---" not in l and not l.lower().startswith("| strategy") and not l.lower().startswith("| variant"):
            cells = [c.strip() for c in l.strip("|").split("|")]
            if len(cells) >= 3:
                verdict = cells[-1]
                cls = "fail" if "FAIL" in verdict else ("park" if "PARK" in verdict else "pass")
                rows.append({"section": section, "cells": cells, "cls": cls})
    return rows, header_note


def main():
    journal = read_jsonl(os.path.join(HERE, "journal.jsonl"))
    equity = read_jsonl(os.path.join(HERE, "equity.jsonl"))
    rows, note = parse_scoreboard(os.path.join(ROOT, "scoreboard.md"))

    # group journal entries into trading days by the 'run' events
    days = []
    cur_orders = []
    for e in journal:
        if e.get("act") == "order":
            cur_orders.append(e)
        elif e.get("act") == "run":
            date = e["t"][:10]
            days.append({"date": date, "equity": e.get("equity"), "dry": e.get("dry"), "decisions": e.get("decisions", []), "orders": cur_orders})
            cur_orders = []
    days.sort(key=lambda d: d["date"], reverse=True)

    data = {
        "generated": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "scoreboard": rows,
        "scoreboard_note": note,
        "days": days,
        "equity": equity,
    }
    payload = json.dumps(data, separators=(",", ":"))
    tpl = open(os.path.join(HERE, "dashboard_template.html"), encoding="utf-8").read()
    html = tpl.replace("__DATA__", payload)
    out = os.path.join(SITE, "index.html")
    open(out, "w", encoding="utf-8").write(html)
    print("wrote", out, len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
