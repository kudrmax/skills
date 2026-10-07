---
name: resume-tailor
description: Tailors NAME LAST_NAME's one-page LaTeX resume (RU/EN) to a job vacancy and returns a compiled PDF plus the .tex for Overleaf. Use this whenever the user pastes a job/vacancy/internship description (hh.ru, LinkedIn, Telegram post, company site), even with no other words, or asks to adapt/tailor/rebuild "my resume/CV/резюме" for a position, company or role. Also use for follow-up tweaks to a resume generated earlier in the chat (swap a project, change the title, switch language, toggle the photo), and when the user explicitly asks for a cover letter / motivation letter / сопроводительное / мотивационное письмо for a vacancy.
---

# Resume tailor

The user pastes a vacancy, you return `LAST_NAME_CV_<Company>_<Role>.pdf` + `.tex`.
All LaTeX lives in templates and is assembled by a script; your job is only to *choose* content
and write a small selection JSON. Keep token use low: do not open `scripts/build.py`,
`templates/`, or the whole `data/content.json` — the catalog command gives you what you need.

## Workflow

1. Run `python /mnt/skills/user/resume-tailor/scripts/build.py catalog` (adjust the path if the skill
   lives elsewhere — the script sits next to this file in `scripts/`). It prints ids of summaries,
   CROC bullets, skill presets, the pool of skills the user actually has, projects with tags,
   available text variants and focus notes, and courses.
2. Analyse the vacancy: role family, must-have and nice-to-have stack, seniority, company and its country.
3. Write `/tmp/selection.json` (schema below). Prefer existing ids/variants; write custom text only
   where it clearly improves the match. For custom project text read only that project's section:
   `grep -A25 "^## <id>" references/projects_facts.md`.
4. Run `python .../scripts/build.py build /tmp/selection.json` (writes to `/mnt/user-data/outputs`).
   The script fits the page by itself: it starts with margins 1.05/1.05/1.365/1.05 in (left/right/top/bottom,
   top ≈ 1.3× sides) and steps through ready presets (1.00/1.30, 0.95/1.24, 0.90/1.17, 0.85/1.11, 0.80/1.04,
   0.75/1.04) until the CV fits on one page; the chosen margins go into both the PDF and the .tex.
   Do not shorten content while margins can still shrink. Only if it prints the "does not fit even with
   the smallest margins" warning, shorten content (drop the weakest project, use shorter variants/summary)
   and rebuild. It also reports LaTeX errors and overfull boxes. Optionally rasterize page 1
   (`pdftoppm -png -r 60`) and look at it once if you changed layout-heavy things.
5. `present_files` with the PDF first, then the .tex. Reply in the user's language (Russian by
   default), very briefly: 2–5 short lines — title chosen, project order, photo on/off, and any
   vacancy requirement the resume cannot honestly cover (so the user can confirm or skip it).

## Decisions

**Language.** Resume language = language of the vacancy text unless the user says otherwise.

**Photo** (`"photo": true/false`). Default true. Turn it off for international companies headquartered in
US/UK/Ireland/Netherlands/Nordics or clearly Western remote-first companies (even if hiring in Serbia).
Keep it on for Russian, Serbian/Balkan, Eastern European and DACH employers, and when unsure.

**File name.** `company`: short Latin name without spaces (VK, Yandex, TBank, Ozon, Sber, HTEC, Nordeus).
`role_abbr`: common initials where they exist — DA (data analyst), PA (product analyst), BA (business analyst),
DS (data scientist), MLE (ML engineer), DE (data engineer), BI (BI analyst/developer), CV / NLP (specialised ML);
otherwise a short word: PyDev, Backend, Quant, Research.

**Title** — the vacancy's role name in a clean form (English titles are normal even in the RU resume, e.g.
"ML Engineer", "Junior Data Scientist"; Russian is fine for Russian-only roles, e.g. "Аналитик данных").
Add "Junior"/"Intern" only if the vacancy is explicitly junior/intern.

**Tagline** — 4–6 items that appear both in the vacancy and in the user's real skills.

**Summary** — an id from the catalog or 2–3 sentences of custom text in the same style
("<Role> с образованием в области прикладной математики и искусственного интеллекта. Имею опыт ...").

**CROC experience** — choose and order bullet ids; you may pass `{"text": "..."}` to rephrase a bullet
toward the vacancy, but only restating the same facts (OLAP cubes, SQL/PostgreSQL on millions of rows,
ETL/automation of data prep, dashboards for business KPIs). Dates/role/company are fixed in data.

**Skills** — a preset id or custom groups `[["Label", "item, item"], ...]`, 4–6 groups, most relevant
group first. Use only items from SKILLS KNOWN. Labels in English (as in the user's resumes) unless using
the `da_ru` preset.

**Projects** — 3–5 most relevant, most relevant first; the page must stay one page.
Rough guide: ML/DS → samokat, bank, yolo (CV roles), liza, onepiece; analyst/BI/DE → bank (data), samokat (data),
liza (data); backend/SWE/Python → bank (eng), samokat (data), mpi, space; HPC/C++ → mpi first.
Titanic and kmeans are fillers. Team projects (samokat, liza) must keep the "в команде / as part of a team" wording.

**Courses** — ids; ШАД is relevant almost always, DLS for ML/DL roles, HSE only if the user asks.

## Honesty rules (important)

The resume is sent to real employers, so every line must be defensible in an interview:
- Never add tools, frameworks, employers, metrics or responsibilities the user does not have. Docker,
  REST/FastAPI/Flask, Superset/DataLens, Airflow in production, Go, JS, CI/CD are NOT confirmed — if the
  vacancy wants them, leave them out and mention the gap in your reply ("если есть опыт с X — скажи, добавлю").
- Never cite metrics from the LizaAlert README (they are marked as invented there) or OnePiece accuracy.
- Numbers in project texts must come from `references/projects_facts.md`.

## selection.json schema

```json
{
  "lang": "ru",                      // "ru" | "en"
  "company": "VK", "role_abbr": "BI",
  "photo": true,
  "title": "Junior Python Developer",
  "tagline": ["Python", "SQL", "PostgreSQL", "BI", "Git"],
  "summary": "da",                   // catalog id OR custom text
  "croc_bullets": ["olap", "sql", "etl", {"text": "custom rephrase"}],
  "skills": "ml",                    // preset id OR [["Programming", "Python, C++, SQL"], ...]
  "projects": ["samokat", {"id": "bank", "variant": "eng"}, {"id": "mpi", "text": "custom"}],
  "courses": ["shad"],
  "section_order": null              // optional override; default RU: education, experience, skills,
                                     // projects, courses, languages; EN: skills, experience, projects,
                                     // education, courses, languages
}
```
Text fields are plain text: `& % # _ $` are escaped automatically, `~` becomes ≈-style `∼`, `--` is an en dash.

## Follow-ups

For tweaks ("убери фото", "поменяй местами проекты", "сделай на английском") edit `/tmp/selection.json`
if it still exists (otherwise rewrite it from the previous reply) and rebuild — do not re-run the catalog.
## Letters (only on explicit request)

A pasted vacancy always means: build the resume. A cover/motivation letter is written ONLY when the user
asks for it in words (same message or later). Then read `references/letters.md` and follow it; the letter
must use the same facts as the resume built in this chat. Do not read that file otherwise.

## Fonts / environment notes

PDFs are compiled with XeLaTeX using CMU (Computer Modern Unicode) fonts from `fonts/` so they look like
the user's Overleaf output. If `fonts/` is empty the script falls back to FreeSerif and prints a warning —
then tell the user the PDF is a preview and the .tex in Overleaf (pdfLaTeX) gives the final look.
The .tex references the photo as `photo_3x4.jpg`, which already exists in the user's Overleaf project.
