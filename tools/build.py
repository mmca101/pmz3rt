import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "questions.csv"
TEMPLATE_PATH = ROOT / "tools" / "template.html"
OUT_PATH = ROOT / "index.html"

KE_RE = re.compile(r"^(\d{2}\.\d{2}\.\d{2})\s+(.*)$")
OPTION_START_RE = re.compile(r"(?:^|\n)\s*[Aa]\)\s")
OPTION_SPLIT_RE = re.compile(r"(?:^|\n)\s*([A-Ea-e])\)\s*")
ANSWER_LETTER_RE = re.compile(r"^\s*([A-Ea-e])\)\s*(.*)$", re.DOTALL)


def normalize_ke(raw):
    raw = raw.strip()
    if raw.lower() == "sonstige":
        return None, "Sonstige"
    m = KE_RE.match(raw)
    if m:
        return m.group(1), m.group(2).strip()
    return None, raw


def parse_mc(frage, antwort):
    m = OPTION_START_RE.search(frage)
    stem = frage[: m.start()].strip()
    options_block = frage[m.start():]
    parts = OPTION_SPLIT_RE.split(options_block)
    # parts[0] is '' (before first letter), then letter, text, letter, text...
    options = []
    for i in range(1, len(parts), 2):
        letter = parts[i].upper()
        text = parts[i + 1].strip() if i + 1 < len(parts) else ""
        text = re.sub(r"\s*\n\s*", " ", text).strip()
        if text:
            options.append({"letter": letter, "text": text})

    am = ANSWER_LETTER_RE.match(antwort.strip())
    correct_letter = am.group(1).upper() if am else None
    return stem, options, correct_letter


def clean_text(t):
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    return t.strip()


def main():
    with CSV_PATH.open(encoding="utf-8") as f:
        rows = list(csv.reader(f))

    header = rows[0]
    data_rows = [r for r in rows[1:] if r and r[0].strip()]

    questions = []
    qid = 1
    ke_seen = {}
    for row in data_rows:
        ke_raw, frage, antwort, info = (row + [""])[:4]
        ke_code, ke_name = normalize_ke(ke_raw)
        ke_key = ke_code or ke_name

        frage = clean_text(frage)
        antwort = clean_text(antwort)
        info = clean_text(info)

        is_mc = bool(OPTION_START_RE.search(frage)) and bool(
            ANSWER_LETTER_RE.match(antwort)
        )

        q = {
            "id": qid,
            "keCode": ke_code,
            "keName": ke_name,
            "keKey": ke_key,
            "info": info,
        }

        if is_mc:
            stem, options, correct = parse_mc(frage, antwort)
            if len(options) >= 2 and correct:
                q["type"] = "mc"
                q["stem"] = stem
                q["options"] = options
                q["correct"] = correct
            else:
                # fallback to open if parsing failed
                q["type"] = "open"
                q["stem"] = frage
                q["answer"] = antwort
        else:
            q["type"] = "open"
            q["stem"] = frage
            q["answer"] = antwort

        questions.append(q)
        ke_seen.setdefault(ke_key, {"code": ke_code, "name": ke_name, "count": 0})
        ke_seen[ke_key]["count"] += 1
        qid += 1

    print(f"Parsed {len(questions)} questions across {len(ke_seen)} competence elements",
          file=sys.stderr)
    for k, v in sorted(ke_seen.items(), key=lambda kv: (kv[1]["code"] or "zzz")):
        print(f"  {v['count']:4d}  {v['code'] or ''} {v['name']}", file=sys.stderr)

    mc_count = sum(1 for q in questions if q["type"] == "mc")
    print(f"MC: {mc_count}  Open: {len(questions) - mc_count}", file=sys.stderr)

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    payload = json.dumps(questions, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")
    out = template.replace("__QUESTIONS_JSON__", payload)
    OUT_PATH.write_text(out, encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({len(out)/1024:.0f} KB)", file=sys.stderr)


if __name__ == "__main__":
    main()
