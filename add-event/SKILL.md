---
name: add-event
description: Turns an event from any input (link, Telegram post, pasted text, screenshot, announcement) into an "add to Apple Calendar" link for iPhone and, in Claude Code, a one-tap Run command that opens it in Calendar on the Mac; plus a Google Calendar link. Use whenever the user drops a link or text about an event, concert, meetup, lecture, party, webinar or any happening and wants it in their calendar — "добавь в календарь", "в календарь", or just a bare link/post with no words. Never guesses the date or time: quotes the source for each, and states plainly what is missing.
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
| Start time | Yes | **Stop.** No event. |
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

## 3. Build the hand-offs (only if nothing blocks)

Event description = the source itself, the ground truth:
- Write the full event text to a temp file verbatim: same words, line breaks, emoji. Do not summarize, translate, reformat or shorten.
- Pasted text or a Telegram post → the whole text as is.
- Web page → only the part about the event, verbatim; drop site chrome (menus, buttons, cookie banners, footers, related links).
- `--url` = the link the user sent, if any; it is appended to the description. Text only, no link → omit `--url`.

```bash
python3 <skill-dir>/scripts/make_links.py \
  --title "..." --start "YYYY-MM-DD HH:MM" [--end "YYYY-MM-DD HH:MM"] \
  --tz Europe/Belgrade --weekday "пятница" \
  --location "..." [--url "<link the user sent>"] --description-file <post.txt> \
  [--out-dir /tmp/add-event]
```

The script prints `WHEN`, `PHONE`, `GOOGLE`, and with `--out-dir` also `ICS` (the file path). If it fails on the weekday check — the date or year is wrong: report it, create nothing.

Hand-offs:
- **iPhone:** the `PHONE` link. It returns a raw .ics, so iOS shows the Apple Calendar add dialog. On a Mac the same link only downloads the file.
- **Mac, Claude Code only:** pass `--out-dir /tmp/add-event` (macOS clears it on its own). **Never open the file yourself** — the user may be away, a sudden Calendar dialog is unwanted. Put the command `open "<ICS>"` in the answer as a single-line ```bash block: the Claude desktop app shows a Run button on it, and Calendar opens the add dialog with a calendar picker when the user taps it.
- **Claude.ai chat:** no Mac hand-off; the `PHONE` link is the one to tap.

## 4. Answer — minimal, no filler

No intro, no retelling of the post, no closing phrases. Exactly this shape (Russian):

````
**<Название>**
📅 <пт, 13.11.2026, 19:00–21:00 (Europe/Belgrade)>
📍 <место>

Из поста:
> <дословная строка с датой/временем>

Допущения:
- <год не указан — взят 2026>
- <конец не указан — +2 ч>

📱 Добавить с телефона:
[Apple Calendar](<PHONE>)

💻 Добавить с ноута:
```bash
open "<ICS>"
```

🌐 Добавить в Google Calendar:
[Google Calendar](<GOOGLE>)
````

Every hand-off is a heading line plus the link or command below it, in this order. Never paste a raw URL — always a short-labelled link. The 💻 block only in Claude Code; in claude.ai drop it.

- Omit "Допущения" if there are none.
- Quotes are verbatim, copied character for character.

If something blocks:

```
❌ Не добавляю: <чего нет — «нет времени начала» / «нет даты» / «две даты, какая?»>

Что есть в посте:
> <дословные строки, относящиеся ко времени, или «ничего о дате/времени»>
```
