#!/usr/bin/env python3
"""Build an .ics file and a Google Calendar link for one event.

Times are given in the event's local timezone and stored in UTC, so any
calendar app shows the correct local time. --weekday cross-checks the date
against the weekday named in the source text and aborts on mismatch.
"""
import argparse
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

WEEKDAYS = {
    "mon": 0, "monday": 0, "пн": 0, "понедельник": 0,
    "tue": 1, "tuesday": 1, "вт": 1, "вторник": 1,
    "wed": 2, "wednesday": 2, "ср": 2, "среда": 2,
    "thu": 3, "thursday": 3, "чт": 3, "четверг": 3,
    "fri": 4, "friday": 4, "пт": 4, "пятница": 4,
    "sat": 5, "saturday": 5, "сб": 5, "суббота": 5,
    "sun": 6, "sunday": 6, "вс": 6, "воскресенье": 6,
}
RU_WEEKDAYS = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--start", required=True, help="'YYYY-MM-DD HH:MM' local time, or 'YYYY-MM-DD' for all-day")
    p.add_argument("--end", help="'YYYY-MM-DD HH:MM' local time")
    p.add_argument("--duration-min", type=int, default=120)
    p.add_argument("--tz", required=True, help="IANA timezone, e.g. Europe/Belgrade")
    p.add_argument("--weekday", help="weekday stated in the source, e.g. 'пятница'")
    p.add_argument("--location", default="")
    p.add_argument("--url", default="")
    p.add_argument("--description", default="")
    p.add_argument("--description-file", help="file with the verbatim event text; overrides --description")
    p.add_argument("--out-dir", default=".")
    return p.parse_args()


def escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line: str) -> str:
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return line
    parts, chunk = [], b""
    for ch in line:
        b = ch.encode("utf-8")
        if len(chunk) + len(b) > 74:
            parts.append(chunk.decode("utf-8"))
            chunk = b""
        chunk += b
    parts.append(chunk.decode("utf-8"))
    return "\r\n ".join(parts)


def slug(text: str) -> str:
    s = re.sub(r"[^\w\-]+", "-", text, flags=re.UNICODE).strip("-")
    return s[:60] or "event"


def main() -> None:
    a = parse_args()
    tz = ZoneInfo(a.tz)
    all_day = len(a.start.strip()) == 10

    if all_day:
        start = datetime.strptime(a.start, "%Y-%m-%d").replace(tzinfo=tz)
        end = start + timedelta(days=1)
    else:
        start = datetime.strptime(a.start, "%Y-%m-%d %H:%M").replace(tzinfo=tz)
        end = (datetime.strptime(a.end, "%Y-%m-%d %H:%M").replace(tzinfo=tz)
               if a.end else start + timedelta(minutes=a.duration_min))
        if end <= start:
            sys.exit("ERROR: end is not after start")

    if a.weekday:
        expected = WEEKDAYS.get(a.weekday.strip().lower().rstrip("."))
        if expected is None:
            sys.exit(f"ERROR: unknown weekday '{a.weekday}'")
        if start.weekday() != expected:
            sys.exit(f"ERROR: {start:%Y-%m-%d} is {RU_WEEKDAYS[start.weekday()]}, "
                     f"but the source says '{a.weekday}'. Date or year is wrong.")

    utc = timezone.utc
    stamp = datetime.now(utc).strftime("%Y%m%dT%H%M%SZ")
    if all_day:
        dt_lines = [f"DTSTART;VALUE=DATE:{start:%Y%m%d}", f"DTEND;VALUE=DATE:{end:%Y%m%d}"]
        g_dates = f"{start:%Y%m%d}/{end:%Y%m%d}"
    else:
        s_utc, e_utc = start.astimezone(utc), end.astimezone(utc)
        dt_lines = [f"DTSTART:{s_utc:%Y%m%dT%H%M%SZ}", f"DTEND:{e_utc:%Y%m%dT%H%M%SZ}"]
        g_dates = f"{s_utc:%Y%m%dT%H%M%SZ}/{e_utc:%Y%m%dT%H%M%SZ}"

    if a.description_file:
        a.description = Path(a.description_file).expanduser().read_text(encoding="utf-8").strip()
    description = "\n\n".join(x for x in [a.description, a.url] if x)
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//add-event//EN", "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT", f"UID:{uuid.uuid4()}@add-event", f"DTSTAMP:{stamp}", *dt_lines,
        f"SUMMARY:{escape(a.title)}",
    ]
    if a.location:
        lines.append(f"LOCATION:{escape(a.location)}")
    if description:
        lines.append(f"DESCRIPTION:{escape(description)}")
    if a.url:
        lines.append(f"URL:{a.url}")
    lines += ["END:VEVENT", "END:VCALENDAR"]

    out_dir = Path(a.out_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{start:%Y-%m-%d}-{slug(a.title)}.ics"
    path.write_text("\r\n".join(fold(l) for l in lines) + "\r\n", encoding="utf-8")

    google = "https://calendar.google.com/calendar/render?" + urlencode({
        "action": "TEMPLATE", "text": a.title, "dates": g_dates,
        "details": description, "location": a.location,
    })
    when = (f"{RU_WEEKDAYS[start.weekday()]}, {start:%d.%m.%Y}, весь день" if all_day else
            f"{RU_WEEKDAYS[start.weekday()]}, {start:%d.%m.%Y}, {start:%H:%M}–{end:%H:%M} ({a.tz})")
    print(f"WHEN: {when}")
    print(f"ICS: {path.resolve()}")
    print(f"GOOGLE: {google}")


if __name__ == "__main__":
    main()
