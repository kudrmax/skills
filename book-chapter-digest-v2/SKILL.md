---
name: book-chapter-digest-v2
description: >-
  Read a real nonfiction / self-help book file (.epub first-class, also .fb2,
  .txt, best-effort .pdf) and write grounded chapter summaries that stand in for
  the chapter itself — the reader may never open the full text. ALWAYS use this
  skill whenever the user uploads or points to a book file and asks to "summarize
  a chapter", "пересказать главу", "выжимка по главе", "краткое содержание главы",
  "стоит ли читать главу N", "что в этой главе", or asks for several chapters at
  once — even if phrased casually or out of order. Also use it for follow-ups
  about the same book (another chapter, a sub-section, "а что в части про X").
  The defining feature: summaries are built strictly from the book's extracted
  text, never from the title or prior knowledge.
---

# Book Chapter Digest v2

Write, for each requested chapter, a **summary that replaces the chapter**.
Assume the reader reads only your summary. If something in it catches their
interest they may open the full chapter, but most of the time they won't. So
after reading the summary they must understand what the author claims, why,
on what evidence, and what to do with it.

The single most important rule: **never summarize from memory, the title, or
general knowledge about the book. Always extract the real chapter text first and
write only from what the extraction returns.** If you can't extract it, say so.

## Setup (once per machine)

The scripts need `lxml`, `markdown` and `pypdf` (only `pypdf` matters here, for
PDF). They live in a shared venv for all skills (never install them globally):

```bash
test -x ~/.claude/skills/.venv/bin/python || \
  (python3 -m venv ~/.claude/skills/.venv && ~/.claude/skills/.venv/bin/pip install lxml markdown pypdf)
```

Always run the scripts with `~/.claude/skills/.venv/bin/python`, never with a
bare `python`/`python3`.

## Workflow

### 1. First contact with a book — build the index (once per book)

The user sends books in **any** format and the structure is **often imperfect** —
a missing or useless table of contents, front/back matter mixed in with real
chapters, one giant undivided blob, or section-divider "chapters" with almost no
text. Treat `build_index.py` as a first pass, not ground truth. Use the path
the user gave (make it absolute).

```bash
~/.claude/skills/.venv/bin/python ~/.claude/skills/book-chapter-digest-v2/scripts/build_index.py "<path-to-book>"
```

This parses the book's own structure (EPUB spine + TOC, FB2 sections, PDF
outline, or TXT headings), writes each chapter's verbatim text to a cache
directory next to the book (`<book-dir>/<book-stem>.digest/`; pass
`--cache-dir "$TMPDIR/<book-stem>.digest"` if that directory is not writable),
prints the chapter table, and emits STRUCTURE SIGNALS when something looks off.
Keep the cache path — every later request reuses it.

If `build_index.py` errors (DRM, scanned/image-only PDF, unsupported format),
say so plainly and stop — never fabricate a summary.

### 1.5. Sanity-check the index before trusting it

Look at the table with judgment — don't assume the rows are clean chapters:

- **Front/back matter** (flagged `служебный?` — Copyright, Dedication, Contents,
  Acknowledgments, Notes, Index…) is not a chapter. When showing the user the
  list, separate real chapters from matter, or at least say which rows are skippable.
- **Tiny rows** (a handful of words) are usually the TOC itself, part dividers, or
  blank pages — not content. Don't summarize them as if they were chapters.
- **Many rows per chapter.** Some books index every sub-heading as its own row.
  Group the rows back into real chapters before summarizing.
- **One huge blob / "not split into chapters" signal** → the book lacks usable
  structure. Don't force it. Tell the user, then offer an alternative: split by
  detectable headings, summarize by logical sections, or ask how to divide it.
- **Suspicious titles** (generic "Section 1", duplicated, or mismatched) → extract
  and glance at the text before trusting the title.

When the structure looks even slightly off, **open the actual text and look**
rather than trusting the index.

### 2. Each request — extract, then summarize

Resolve the request to chapter numbers and extract the real text:

```bash
~/.claude/skills/.venv/bin/python ~/.claude/skills/book-chapter-digest-v2/scripts/extract_chapter.py "<cache-dir>" 5          # one chapter
~/.claude/skills/.venv/bin/python ~/.claude/skills/book-chapter-digest-v2/scripts/extract_chapter.py "<cache-dir>" 5-7        # range
~/.claude/skills/.venv/bin/python ~/.claude/skills/book-chapter-digest-v2/scripts/extract_chapter.py "<cache-dir>" 2,5,9      # specific list
~/.claude/skills/.venv/bin/python ~/.claude/skills/book-chapter-digest-v2/scripts/extract_chapter.py "<cache-dir>" --title "habits"
~/.claude/skills/.venv/bin/python ~/.claude/skills/book-chapter-digest-v2/scripts/extract_chapter.py "<cache-dir>" --list     # show chapters again
```

Read the printed text in full, then write the summary **from that text only**,
using the template and writing rules below.

### 3. Handle a non-linear, inconsistent user

- **Multiple chapters at once** — extract them in one call, one summary block
  each, with a one-line overview at the top.
- **Out-of-order / follow-up requests** ("теперь 2 и 3", "а ещё последнюю") — the
  index is cached, so just extract and summarize. Never ask them to re-upload.
- **Sub-chapter / "the part about X"** — extract the whole chapter, locate the
  relevant section inside the extracted text, and summarize just that part.
- **"Should I read chapter N?"** — answer with the last section of the template
  first, then the summary.
- **Vague reference** ("ту главу про дисциплину") — use `--title` or scan the
  index titles; if genuinely ambiguous, show the candidates and ask which.

## Output language

Write in **the same language as the book** — detect it from the extracted text,
not from the title. Switch only if the user explicitly asks for another
language. Don't ask the user which language to use.

The template below uses English labels. Render the labels in the summary's
language (for a Russian book: «Коротко», «Содержание», «Что можно применить»,
«Стоит ли читать главу целиком?»).

## Template

```
## Chapter N — "Exact title from the book"
~W words · ~M min read

📌 **In short:** <one or two plain sentences: the chapter's main claim and why it matters>

**Summary:**

<The body. It follows the chapter's own line of argument, in order. It is made
of numbered points. Each point opens with a bold headline that is itself a full
sentence, followed by plain explanatory sentences. Nested lists are used where
the chapter has parallel items (terms, steps, studies).>

**What you can apply:**
- <a technique, exercise or rule from the chapter, described fully enough to do
  it without the book: what to do, how often, what to watch for>
- <"—" if the chapter contains nothing practical>

**Should you read the full chapter?** 🟢 yes / 🟡 parts of it / 🔴 the summary is enough
<One or two sentences: what the full text gives beyond this summary (long case
stories, more studies, the author's personal history) and who would want it.
Name the sections worth opening.>
```

For multiple chapters, prepend a one-line map, e.g.:
`Chapters 4–6: 4 — 🟢, 5 — 🔴, 6 — 🟡. Details below.`

If the user explicitly asks for a shorter version («короче»), keep the same
writing rules and cut to «In short» + the bold headlines of the summary points
+ the last section.

## What goes into the summary

The summary is the reader's only copy of the chapter. Its content is decided by
one question: **what does a reader need to understand this chapter and retell it
correctly?**

That includes:

- **The argument, step by step.** The claim, the reasons the author gives, and
  what follows from it. Keep every reasoning step the author takes, including the
  "why this matters" step.
- **The evidence the argument rests on.** Studies, numbers and experiments that
  the author uses as proof, with enough context to know what was measured and
  what was found.
- **The examples and stories that carry an idea.** If the author explains a
  concept through a case, a person or an anecdote, the summary keeps the case
  that explains it best, retold in a sentence or two, with its point made
  explicit.
- **People, with who they are.** Researchers, historical figures and characters
  appear by name together with a few words on who they are and what they
  contributed ("the psychologist Nick Humphrey argues that…").
- **The book's own terms**, each introduced once in a full sentence that says
  what it means, then reused under the same name.
- **Every practical technique**, in "What you can apply", in full.

A summary retells the chapter at the level of its ideas, not paragraph by
paragraph. Each idea appears once, in its clearest form: the claim, the reason,
the strongest piece of evidence or the best example. When the author piles up
several examples or studies for the same point, the summary keeps the one that
makes the point best and may say that there are more.

What stays out is material that carries no idea: the history of how the book or
the field got funded, who asked the author a question and in which year,
publishing anecdotes, lists of people thanked, digressions the author himself
marks as off-topic.

There is no fixed length. Length follows the number of distinct ideas in the
chapter, not its word count: a long chapter built from stories can have a short
summary. As an orientation, a typical chapter comes out at roughly a tenth to a
sixth of its own length. If the summary is far longer, it is probably retelling
paragraphs rather than ideas.

## How the summary reads

Write for a reader who reads the summary once, at normal speed, possibly in
their second language, possibly on an e-reader screen. Every sentence should be
understood on the first pass.

A good summary sentence looks like this:

- it has a subject and a verb, with ordinary articles and connecting words;
- it says one thing;
- when it relates two ideas, the relation is a word — *because*, *so*, *but*,
  *for example*, *which means*, *in other words* — rather than a dash, colon,
  semicolon or bracket;
- the main point is in the main clause, and a bracket holds only something the
  reader can skip;
- numbers are written the way a person would say them in a sentence ("more than
  70 percent of the score"), next to what they measure;
- names, allusions and references come with the context needed to understand
  them;
- it uses common words, and the book's own terms once they are introduced.

A bullet point is one or more such sentences. A bold headline is also a full
sentence that states the point ("**The old theory had three parts and three
flaws.**"), not a label.

Before returning, reread the summary as a reader who has not seen the book.
Wherever you have to go back to work out what belongs to what, split the
sentence, turn the bracket into its own sentence, or name the relation in words.

### Example

The same point written as notes and written as a summary.

**Notes (hard to read, loses the reasoning):**

> **Relationships** — "other people," as Christopher Peterson put it; Seligman
> argues yes from evolution: the big brain as a social problem-solver (Nick
> Humphrey) and group selection (E. O. and D. S. Wilson) — groups with "hive
> emotions" (love, compassion, teamwork) out-compete others.

**Summary (same facts, one reading is enough):**

> **Positive relationships are the third element.** Christopher Peterson, one of
> the founders of positive psychology, once summed up the whole field in two
> words: "Other people." Almost all the high points of our lives happen around
> other people. The open question is whether we seek relationships for their own
> sake, or only because they bring pleasure or success. Seligman admits that he
> does not know for sure. He leans towards "for their own sake" because of two
> arguments from evolution.
> - The psychologist Nick Humphrey argues that the human brain grew large mainly
>   to solve social problems.
> - The biologists E. O. Wilson and D. S. Wilson argue that natural selection
>   works on whole groups, not only on individuals. A group with "hive emotions"
>   such as love, compassion and teamwork cooperates better than a group without
>   them, so it wins and its genes survive.
>
> So relationships matter so much for survival that evolution made them
> pleasant and meaningful to make sure we seek them.

The same applies in any language. A Russian summary is written in the same
full sentences, with words for the relations:

> **Здоровье авторы понимают широко.** Это не только тело, но и ум, и дух.
> Дух при этом не обязательно религиозный.

## Grounding rules (do not violate)

- **Read before you write.** Run `extract_chapter.py` and read its output before
  composing any summary. No extraction → no summary.
- **Every specific comes from the text.** Names, claims, numbers, steps and any
  quoted phrase come from the extracted text, not from memory. This limits what
  you may write; it does not oblige you to include every specific.
- **Connecting words follow the author.** A *because* or *so* you add states a
  link the author makes. Rewording for clarity never adds a claim.
- **The last section is grounded too.** What the full chapter adds beyond the
  summary is based on what the extracted text actually contains.
- **If the extraction is thin, garbled, or empty, say so** instead of guessing
  the content.
- **Titles can mislead.** Trust the extracted text over the title every time.

## Format support

| Format | Reliability | Notes |
|--------|-------------|-------|
| `.epub` | First-class | Splits by TOC (NCX or nav), handles multiple chapters per file via anchors. |
| `.fb2`  | Good | Splits by `<section>` + `<title>`. |
| `.txt`  | Best-effort | Splits on heading lines (Глава/Chapter/Часть/…). |
| `.pdf`  | Best-effort | Uses bookmarks/outline if present; else heading detection. Needs `pypdf` from the skills venv (see Setup). Scanned/image PDFs won't work without OCR. |

If a book is `.mobi`/`.azw3`, ask the user to convert it to EPUB (e.g. Calibre).

## Scripts

Both live in `~/.claude/skills/book-chapter-digest-v2/scripts/` and run with
`~/.claude/skills/.venv/bin/python`.

- `scripts/build_index.py <book> [--cache-dir DIR]` — parse the book, cache real
  chapter text, print the chapter table. Run once per book.
- `scripts/extract_chapter.py <cache-dir> <selectors...> [--title S] [--list]` —
  print the verbatim text of selected chapters. Selectors accept ranges (`8-15`).
  Run before every summary.
