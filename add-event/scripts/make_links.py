#!/usr/bin/env python3
"""Build "add to calendar" hand-offs for one event.

PHONE:  https link to ics.agical.io, which answers with a raw text/calendar file;
        iPhone opens the Apple Calendar add dialog straight from it.
ICS:    the same event as a local .ics file (with --out-dir); on a Mac opening it
        shows the Calendar add dialog with a calendar picker.
GOOGLE: Google Calendar template link.

Times are given in the event's local timezone and sent in UTC. --weekday
cross-checks the date against the weekday named in the source and aborts on mismatch.
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
ICS_UTC = "%Y%m%dT%H%M%SZ"


class Event:
    def __init__(self, title: str, start: datetime, end: datetime, location: str, description: str):
        self.title = title
        self.start = start
        self.end = end
        self.location = location
        self.description = description
        self.start_utc = start.astimezone(timezone.utc)
        self.end_utc = end.astimezone(timezone.utc)

    def phone_link(self) -> str:
        return "https://ics.agical.io/?" + urlencode({
            "subject": self.title,
            "dtstart": self.start_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "dtend": self.end_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "location": self.location,
            "description": self.description,
            "reminder": "0",
        })

    def google_link(self) -> str:
        return "https://calendar.google.com/calendar/render?" + urlencode({
            "action": "TEMPLATE", "text": self.title,
            "dates": f"{self.start_utc:{ICS_UTC}}/{self.end_utc:{ICS_UTC}}",
            "details": self.description, "location": self.location,
        })

    def ics(self) -> str:
        lines = [
            "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//add-event//EN", "CALSCALE:GREGORIAN",
            "BEGIN:VEVENT", f"UID:{uuid.uuid4()}@add-event",
            f"DTSTAMP:{datetime.now(timezone.utc):{ICS_UTC}}",
            f"DTSTART:{self.start_utc:{ICS_UTC}}", f"DTEND:{self.end_utc:{ICS_UTC}}",
            f"SUMMARY:{_escape(self.title)}",
        ]
        if self.location:
            lines.append(f"LOCATION:{_escape(self.location)}")
        if self.description:
            lines.append(f"DESCRIPTION:{_escape(self.description)}")
        lines += ["END:VEVENT", "END:VCALENDAR"]
        return "\r\n".join(_fold(l) for l in lines) + "\r\n"

    def file_name(self) -> str:
        slug = re.sub(r"[^\w\-]+", "-", self.title, flags=re.UNICODE).strip("-")[:60] or "event"
        return f"{self.start:%Y-%m-%d}-{slug}.ics"

    def when(self, tz_name: str) -> str:
        return (f"{RU_WEEKDAYS[self.start.weekday()]}, {self.start:%d.%m.%Y}, "
                f"{self.start:%H:%M}–{self.end:%H:%M} ({tz_name})")


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _fold(line: str) -> str:
    parts, chunk = [], b""
    for ch in line:
        b = ch.encode("utf-8")
        if len(chunk) + len(b) > 74:
            parts.append(chunk.decode("utf-8"))
            chunk = b""
        chunk += b
    parts.append(chunk.decode("utf-8"))
    return "\r\n ".join(parts)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--start", required=True, help="'YYYY-MM-DD HH:MM' local time")
    p.add_argument("--end", help="'YYYY-MM-DD HH:MM' local time")
    p.add_argument("--duration-min", type=int, default=120)
    p.add_argument("--tz", required=True, help="IANA timezone, e.g. Europe/Belgrade")
    p.add_argument("--weekday", help="weekday stated in the source, e.g. 'пятница'")
    p.add_argument("--location", default="")
    p.add_argument("--url", default="", help="link the user sent; appended to the description")
    p.add_argument("--description-file", help="file with the verbatim event text")
    p.add_argument("--out-dir", help="also write the .ics file here")
    return p.parse_args()


def check_weekday(start: datetime, stated: str) -> None:
    expected = WEEKDAYS.get(stated.strip().lower().rstrip("."))
    if expected is None:
        sys.exit(f"ERROR: unknown weekday '{stated}'")
    if start.weekday() != expected:
        sys.exit(f"ERROR: {start:%Y-%m-%d} is {RU_WEEKDAYS[start.weekday()]}, "
                 f"but the source says '{stated}'. Date or year is wrong.")


def main() -> None:
    a = parse_args()
    tz = ZoneInfo(a.tz)
    start = datetime.strptime(a.start, "%Y-%m-%d %H:%M").replace(tzinfo=tz)
    end = (datetime.strptime(a.end, "%Y-%m-%d %H:%M").replace(tzinfo=tz)
           if a.end else start + timedelta(minutes=a.duration_min))
    if end <= start:
        sys.exit("ERROR: end is not after start")
    if a.weekday:
        check_weekday(start, a.weekday)

    text = Path(a.description_file).expanduser().read_text(encoding="utf-8").strip() if a.description_file else ""
    event = Event(a.title, start, end, a.location, "\n\n".join(x for x in [text, a.url] if x))

    print(f"WHEN: {event.when(a.tz)}")
    print(f"PHONE: {event.phone_link()}")
    if a.out_dir:
        path = (Path(a.out_dir).expanduser() / event.file_name()).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(event.ics(), encoding="utf-8")
        print(f"ICS: {path}")
    print(f"GOOGLE: {event.google_link()}")


if __name__ == "__main__":
    main()
