import csv
import io
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "questions.csv"
TEMPLATE_PATH = ROOT / "tools" / "template.html"
OUT_PATH = ROOT / "index.html"

# Google Sheets export endpoint. This is a server-side fetch (plain HTTP
# request from this script), not a browser fetch() call from the deployed
# page — so none of the CORS/reliability concerns that rule out live
# client-side loading apply here. Requires the sheet to stay shared as
# "anyone with the link can view".
SHEET_ID = "11t6Mg6wWiLrnGqrYuuEANyK9gU4s6C4gBeuNBn5-G3E"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"


def load_rows():
    """Fetch the question bank straight from the Google Sheet. Falls back to
    the last-known-good local copy (data/questions.csv) if the sheet can't be
    reached, and refreshes that local copy on every successful fetch so it
    stays a working snapshot even if the sheet later goes away."""
    try:
        req = urllib.request.Request(SHEET_CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read()
        text = raw.decode("utf-8")
        rows = list(csv.reader(io.StringIO(text)))
        if not rows or not rows[0]:
            raise ValueError("empty response from sheet")
        CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        CSV_PATH.write_text(text, encoding="utf-8", newline="")
        print(f"Fetched question bank live from Google Sheets ({len(rows)} rows)", file=sys.stderr)
        return rows
    except (urllib.error.URLError, TimeoutError, ValueError, UnicodeDecodeError) as e:
        print(f"Warning: couldn't fetch sheet live ({e}); falling back to {CSV_PATH}", file=sys.stderr)
        with CSV_PATH.open(encoding="utf-8") as f:
            return list(csv.reader(f))

KE_RE = re.compile(r"^(\d{2}\.\d{2}\.\d{2})\s+(.*)$")

# An MC option marker is either a letter (A-F) or a digit (1-6), followed by
# ')' or '.', then whitespace — covers "A)", "a)", "A.", "1)", "1." etc. The
# marker TYPE (letter vs digit) must stay consistent within one question's
# option list, but the separator ('.' vs ')') doesn't have to.
OPTION_START_RE = re.compile(r"(?:^|\n)[ \t]*([Aa]|1)[.\)][ \t]+")
OPTION_SPLIT_LETTER_RE = re.compile(r"(?:^|\n)[ \t]*([A-Fa-f])[.\)][ \t]*")
OPTION_SPLIT_DIGIT_RE = re.compile(r"(?:^|\n)[ \t]*([1-6])[.\)][ \t]*")
ANSWER_MARKER_RE = re.compile(r"^[ \t]*([A-Fa-f]|[1-6])[.\)][ \t]*(.*)$", re.DOTALL)
DIGIT_TO_LETTER = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "E", "6": "F"}


def normalize_marker(raw):
    return DIGIT_TO_LETTER[raw] if raw.isdigit() else raw.upper()


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
    is_digit_scheme = m.group(1).isdigit()
    split_re = OPTION_SPLIT_DIGIT_RE if is_digit_scheme else OPTION_SPLIT_LETTER_RE
    parts = split_re.split(options_block)
    # parts[0] is '' (before first marker), then marker, text, marker, text...
    options = []
    for i in range(1, len(parts), 2):
        letter = normalize_marker(parts[i])
        text = parts[i + 1].strip() if i + 1 < len(parts) else ""
        text = re.sub(r"\s*\n\s*", " ", text).strip()
        if text:
            options.append({"letter": letter, "text": text})

    am = ANSWER_MARKER_RE.match(antwort.strip())
    correct_letter = normalize_marker(am.group(1)) if am else None
    return stem, options, correct_letter


def clean_text(t):
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    return t.strip()


def main():
    rows = load_rows()
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
            ANSWER_MARKER_RE.match(antwort)
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
