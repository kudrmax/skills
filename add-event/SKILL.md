---
name: add-event
description: Turns an event from any input (link, Telegram post, pasted text, screenshot, announcement) into a calendar entry — an .ics file that opens in Apple Calendar with a calendar picker, plus a Google Calendar link. Use whenever the user drops a link or text about an event, concert, meetup, lecture, party, webinar or any happening and wants it in their calendar — "добавь в календарь", "в календарь", or just a bare link/post with no words. Never guesses the date or time: quotes the source for each, and states plainly what is missing.
---

# Event → calendar

The cost of a wrong date is high. A missing event is better than a wrong one. Every fact in the event must come from the source and be quoted.

## 1. Get the text

- Text or screenshot pasted → use it as is.
- Telegram link `t.me/<channel>/<id>` → fetch `https://t.me/<channel>/<id>?embed=1&mode=tme`. The post text is in `div.tgme_widget_message_text`; the publication date is the `datetime="..."` attribute. In Claude Code this works with `curl -sL`.
- Any other link → fetch the page with the web fetch tool (or `curl`).
- Could not read the page (login wall, Instagram, error) → say so in one line and ask to paste the text. Do not reconstruct the event from the URL, title or memory.

Remember the **publication date** of the post: it anchors the year and relative words ("завтра", "в эту субботу").

## 2. Extract, and classify every field

| Field | Must be in source? | If missing |
|---|---|---|
| Date (day + month) | Yes | **Stop.** No event. |
| Start time | Yes | **Stop.** No event (all-day only if the user asks). |
| Year | No | Nearest future date after publication. Flag it. |
| Weekday | No | If present, pass it to `--weekday` — the script rejects a mismatch. |
| End time / duration | No | 2 hours. Flag it. |
| Timezone | No | From the city/address. Flag it. Unknown city → **stop**. |
| Title, place | No | Short title from the post; place as written. |

Rules:
- "Сбор гостей в 19:00", "двери в 19:00", "начало в 19:30" — use the time that is written, and quote it. If both doors and start are given, the start is the event start.
- Several dates or sessions → list them and ask which one; do not pick.
- Relative dates ("завтра", "в субботу") → resolve against the publication date, and flag the resolution.
- Date already in the past relative to today → say so, do not create.
- Any doubt about a value → it is missing, not guessed.

## 3. Build the file (only if nothing blocks)

```bash
python3 <skill-dir>/scripts/make_ics.py \
  --title "..." --start "YYYY-MM-DD HH:MM" [--end "YYYY-MM-DD HH:MM"] \
  --tz Europe/Belgrade --weekday "пятница" \
  --location "..." [--url "<link the user sent>"] --description-file <post.txt> \
  --out-dir <dir>
```

Event description = the source itself, the ground truth:
- Write the full event text to `<post.txt>` verbatim: same words, line breaks, emoji. Do not summarize, translate, reformat or shorten.
- Pasted text or a Telegram post → the whole text as is.
- Web page → only the part about the event, verbatim; drop site chrome (menus, buttons, cookie banners, footers, related links).
- `--url` = the link the user sent, if any; the script appends it to the description. Text only, no link → omit `--url`.

The script prints `WHEN`, `ICS` and `GOOGLE`. If it fails on the weekday check — the date or year is wrong: report it, create nothing.

Where to put the file and how to hand it over:
- **Claude Code (macOS):** `--out-dir ~/Downloads`, then run `open <ICS path>`. Calendar opens a dialog where the user picks the calendar and confirms; nothing is saved without that click.
- **Claude.ai chat:** `--out-dir /mnt/user-data/outputs` and present the file for download. On iPhone/Mac tapping the .ics opens the Calendar add dialog with a calendar picker.
- Always also give the Google Calendar link as a fallback.

## 4. Answer — minimal, no filler

No intro, no retelling of the post, no closing phrases. Exactly this shape (Russian):

```
**<Название>**
📅 <пт, 13.11.2026, 19:00–21:00 (Europe/Belgrade)>
📍 <место>

Из поста:
> <дословная строка с датой/временем>

Допущения:
- <год не указан — взят 2026>
- <конец не указан — +2 ч>

<Календарь открыт — выбери календарь в диалоге | файл .ics>
[Google Calendar](<GOOGLE>)
```

- Omit "Допущения" if there are none.
- Quotes are verbatim, copied character for character.

If something blocks:

```
❌ Не добавляю: <чего нет — «нет времени начала» / «нет даты» / «две даты, какая?»>

Что есть в посте:
> <дословные строки, относящиеся ко времени, или «ничего о дате/времени»>
```
