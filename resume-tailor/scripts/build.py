#!/usr/bin/env python3
"""Resume builder for the resume-tailor skill.

Usage:
  python build.py catalog                 # compact list of ids for choosing content
  python build.py build selection.json [--out DIR] [--no-pdf]

Outputs <file_prefix>_<company>_<role>.tex (for Overleaf, pdfLaTeX preamble) and,
unless --no-pdf, the same-named .pdf compiled locally with XeLaTeX.
"""
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data/content.json").read_text(encoding="utf-8"))
PROF = json.loads((ROOT / "data/profile.json").read_text(encoding="utf-8"))
PREAMBLE = (ROOT / "templates/preamble.tex").read_text(encoding="utf-8")

# Margin presets (left, right, top, bottom) in inches, tried in order until the CV fits on one page.
MARGINS = [(1.05, 1.05, 1.365, 1.05), (1.00, 1.00, 1.30, 1.00), (0.95, 0.95, 1.24, 0.95),
           (0.90, 0.90, 1.17, 0.90), (0.85, 0.85, 1.11, 0.85), (0.80, 0.80, 1.04, 0.80),
           (0.75, 0.75, 1.04, 0.75)]


def geometry(m):
    l, r, t, b = m
    return f"\\usepackage[a4paper, left={l:.2f}in, right={r:.2f}in, top={t:.3f}in, bottom={b:.2f}in]{{geometry}}"


PRE_SPACE = {"education": "-7pt", "experience": "-7pt", "skills": "-8pt",
             "projects": "-7pt", "courses": "-7pt", "languages": "-6pt"}


def esc(s: str) -> str:
    """Escape LaTeX specials that are not already escaped. Backslash commands pass through."""
    s = re.sub(r"(?<!\\)([&%#_$])", r"\\\1", s)
    return re.sub(r"(?<!\\)~", r"$\\sim$", s)


def pick(obj, lang):
    if isinstance(obj, dict) and lang in obj:
        return obj[lang]
    return obj


# ---------------------------------------------------------------- catalog
def catalog():
    out = []
    out.append("SUMMARIES: " + ", ".join(DATA["summaries"]))
    cr = DATA["experience"]["croc"]
    out.append("CROC BULLETS: " + ", ".join(cr["bullets"]) + "  (default: " + ",".join(cr["default_bullets"]) + ")")
    out.append("SKILL PRESETS:")
    for k, groups in DATA["skill_presets"].items():
        out.append(f"  {k}: " + " | ".join(g[0] for g in groups))
    out.append("SKILLS KNOWN (pool for custom groups): " + DATA["skills_known"])
    out.append("SKILLS UNCONFIRMED: " + DATA["skills_unconfirmed"])
    out.append("PROJECTS (id [tags] date :: variants :: focus):")
    for pid, p in DATA["projects"].items():
        out.append(f"  {pid} [{', '.join(p['tags'])}] {p['date']['en']} :: {','.join(p['variants'])} :: {p['focus']}")
    out.append("COURSES: " + ", ".join(DATA["courses"]) + "  (default: " + ",".join(DATA["courses_default"]) + ")")
    print("\n".join(out))


# ---------------------------------------------------------------- body parts
def header(sel, lang):
    name = PROF["name"][lang]
    parts = []
    for c in PROF["contacts"][lang]:
        if c.get("url") is None:
            parts.append(("\\small " if c.get("small") else "") + c["label"])
        elif c.get("link_part"):
            pre = c["label"].replace(c["link_part"], "")
            parts.append(f"{pre}\\href{{{c['url']}}}{{\\underline{{{c['link_part']}}}}}")
        else:
            parts.append(f"\\href{{{c['url']}}}{{\\underline{{{c['label']}}}}}")
    contacts = "\n                $|$\n                ".join(parts)
    title = esc(sel["title"])
    tagline = " \\textbar{} ".join(esc(t) for t in sel["tagline"])
    summ = sel["summary"]
    summary = esc(DATA["summaries"][summ][lang]) if summ in DATA["summaries"] else esc(summ)
    sec = PROF["sections"][lang]["summary"]
    return f"""
% ----- ФОТО + ЗАГОЛОВОК ------
\\begin{{tabular}}{{@{{}} l @{{\\hspace{{\\indentAfterPhoto}}}} l}}
    \\ifwithphoto
        \\includegraphics[width=\\photoWidth]{{{PROF['photo_file']}}} &
    \\fi
        \\begin{{minipage}}[t]{{\\headerWidth}}
            \\vspace{{\\vspaceHeader}}

            \\begin{{center}}
                \\textbf{{\\Huge \\scshape {name}}} \\\\ \\vspace{{4pt}}
                {contacts}
                \\\\

                \\vspace{{11pt}}

                \\textbf{{\\LARGE \\scshape {title}}}

                \\vspace{{2pt}}

                \\small {tagline}

                \\vspace{{-11pt}}

            \\end{{center}}

            \\section{{{sec}}}

            \\noindent
            \\hspace*{{\\tabLeftSummary}}
            \\begin{{minipage}}{{\\dimexpr \\summaryWidth \\textwidth-\\tabLeftSummary\\relax}}
            \\small

            {summary}

            \\end{{minipage}}

        \\end{{minipage}}
\\end{{tabular}}
"""


def sec_education(sel, lang):
    rows = []
    for e in PROF["education"]:
        d = e[lang]
        rows.append(f"\\resumeSubheading\n    {{{d['uni']}}}{{{e['years']}}}\n    {{{d['degree']}}}{{{d['city']}}}\n")
    return "\\resumeSubHeadingListStart\n\n" + "\n".join(rows) + "\n\\resumeSubHeadingListEnd\n"


def sec_experience(sel, lang):
    cr = DATA["experience"]["croc"]
    items = []
    for b in sel.get("croc_bullets", cr["default_bullets"]):
        if isinstance(b, dict):
            txt = esc(b["text"])
        else:
            txt = esc(cr["bullets"][b][lang])
        items.append(f"\\resumeItem{{\n{txt}\n}}\n")
    return (f"\\vspace{{2pt}}\n\n\\resumeSubHeadingListStart\n\n"
            f"\\resumeSubheading\n    {{{cr['role'][lang]}}}{{{cr['dates'][lang]}}}\n"
            f"    {{\\href{{{cr['url']}}}{{{cr['company'][lang]}}}}}{{{cr['city'][lang]}}}\n\n"
            f"\\vspace{{3pt}}\n\n\\resumeItemListStart\n\n" + "\n".join(items) +
            "\n\\resumeItemListEnd\n\n\\resumeSubHeadingListEnd\n")


def sec_skills(sel, lang):
    groups = sel["skills"]
    if isinstance(groups, str):
        groups = DATA["skill_presets"][groups]
    out = ["\\vspace{2pt}\n"]
    for label, items in groups:
        out.append(f"\\resumeSkillString[0.39in]\n{{\n\\textbf{{{esc(label)}:}}\n{esc(items)}\n}}\n")
    return "\n".join(out)


def sec_projects(sel, lang):
    out = ["    \\vspace{2pt}\n    \\resumeSubHeadingListStart\n"]
    for p in sel["projects"]:
        if isinstance(p, str):
            p = {"id": p}
        pr = DATA["projects"][p["id"]]
        if "text" in p:
            text = esc(p["text"])
        else:
            text = esc(pr["variants"][p.get("variant", "default")][lang])
        title = esc(p.get("title", pr["title"][lang]))
        tags = p.get("tags", pr["tags"])
        boxes = " ".join(f"\\skillbox{{{esc(t)}}}" for t in tags)
        out.append(f"""
    % {p['id'].upper()}
    \\resumeProjectHeading
        {{\\textbf{{{title}}} $|$ \\href{{{pr['url']}}}{{\\underline{{GitHub}}}} $|$ {boxes}}}{{{pr['date'][lang]}}}
        \\projectSummary{{{text}}}
""")
    out.append("\n    \\resumeSubHeadingListEnd\n")
    return "".join(out)


def sec_courses(sel, lang):
    ids = sel.get("courses", DATA["courses_default"])
    return "\n".join(f"\\resumeSkillString[0.39in]\n{{{DATA['courses'][c][lang]}}}\n" for c in ids)


def sec_languages(sel, lang):
    return f"\\vspace{{4pt}}\n\n\\resumeSkillString[0.39in]\n{{\n{PROF['languages'][lang]}\n}}\n"


SECTIONS = {"education": sec_education, "experience": sec_experience, "skills": sec_skills,
            "projects": sec_projects, "courses": sec_courses, "languages": sec_languages}


def body(sel, lang):
    parts = ["\\begin{document}\n", header(sel, lang)]
    order = sel.get("section_order", PROF["section_order"][lang])
    for i, s in enumerate(order):
        if s == "courses" and not sel.get("courses", DATA["courses_default"]):
            continue
        sp = "-4pt" if i == 0 else PRE_SPACE[s]
        parts.append(f"\n\n\\vspace{{{sp}}}\n\n\\section{{{PROF['sections'][lang][s]}}}\n\n")
        parts.append(SECTIONS[s](sel, lang))
    parts.append("\n\\end{document}\n")
    return "".join(parts)


# ---------------------------------------------------------------- preambles
def preamble(engine, lang, photo, margins=MARGINS[0]):
    if engine == "pdflatex":
        babel = "[russian,english]" if lang == "en" else "[english,russian]"
        a = "\\input{glyphtounicode}"
        b = f"\\usepackage[utf8x]{{inputenc}}\n\\usepackage{babel}{{babel}}\n\\usepackage{{cmap}}"
        c = "% Ensure that generate pdf is machine readable/ATS parsable\n\\pdfgentounicode=1"
    else:
        fonts = ROOT / "fonts"
        a = ""
        if (fonts / "cmunrm.otf").exists():
            fontdef = ("\\setmainfont{cmunrm.otf}[Path=" + str(fonts) + "/, "
                       "BoldFont=cmunbx.otf, ItalicFont=cmunti.otf, BoldItalicFont=cmunbi.otf]")
        else:
            fontdef = "\\setmainfont{FreeSerif} % FALLBACK: CMU fonts not found in fonts/"
        main, other = ("english", "russian") if lang == "en" else ("russian", "english")
        b = (f"\\usepackage{{fontspec}}\n{fontdef}\n\\usepackage{{polyglossia}}\n"
             f"\\setmainlanguage{{{main}}}\n\\setotherlanguage{{{other}}}")
        c = ""
    flag = "\\withphototrue  % флаг включён" if photo else "\\withphotofalse % флаг выключен"
    return (PREAMBLE.replace("%%ENGINE_A%%", a).replace("%%ENGINE_B%%", b)
            .replace("%%ENGINE_C%%", c).replace("%%PHOTO_FLAG%%", flag)
            .replace("%%GEOMETRY%%", geometry(margins)))


# ---------------------------------------------------------------- build
def compile_xe(td, tex):
    (td / "cv.tex").write_text(tex, encoding="utf-8")
    subprocess.run(["xelatex", "-interaction=nonstopmode", "cv.tex"], cwd=td, capture_output=True, text=True)
    log = (td / "cv.log").read_text(errors="ignore")
    m = re.search(r"Output written on .*?\((\d+) page", log)
    return (int(m.group(1)) if m else 0), log


def build(sel_path, out_dir, make_pdf=True):
    sel = json.loads(Path(sel_path).read_text(encoding="utf-8"))
    lang = sel["lang"]
    photo = bool(sel.get("photo", True))
    stem = f"{PROF['file_prefix']}_{sel['company']}_{sel['role_abbr']}"
    stem = re.sub(r"[^\w\-]", "", stem.replace(" ", ""))
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    b = body(sel, lang)
    tex_path = out_dir / f"{stem}.tex"

    if not make_pdf:
        tex_path.write_text(preamble("pdflatex", lang, photo) + "\n" + b, encoding="utf-8")
        print(f"TEX: {tex_path}  margins={MARGINS[0]} (not checked, --no-pdf)")
        return
    if not (ROOT / "fonts/cmunrm.otf").exists():
        print("WARNING: CMU fonts missing in fonts/ -> PDF uses fallback FreeSerif (preview only).")
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        shutil.copy(ROOT / "assets" / PROF["photo_file"], td / PROF["photo_file"])
        chosen, pages = MARGINS[-1], 0
        for m in MARGINS:                      # shrink margins step by step until 1 page
            pages, _ = compile_xe(td, preamble("xelatex", lang, photo, m) + "\n" + b)
            if pages == 1:
                chosen = m
                break
        else:
            chosen = MARGINS[-1]
        pages, log = compile_xe(td, preamble("xelatex", lang, photo, chosen) + "\n" + b)  # final pass
        errs = [l for l in log.splitlines() if l.startswith("!")]
        if not (td / "cv.pdf").exists():
            print("ERROR: PDF not produced\n" + "\n".join(errs[:10])); sys.exit(1)
        tex_path.write_text(preamble("pdflatex", lang, photo, chosen) + "\n" + b, encoding="utf-8")
        pdf_path = out_dir / f"{stem}.pdf"
        shutil.copy(td / "cv.pdf", pdf_path)
        over = len(re.findall(r"Overfull \\hbox \((\d+\.\d+)pt", log))
        print(f"TEX: {tex_path}")
        print(f"PDF: {pdf_path}  pages={pages}  margins(l,r,t,b)={chosen}  "
              f"preset={MARGINS.index(chosen)+1}/{len(MARGINS)}  latex_errors={len(errs)}  overfull_boxes={over}")
        if errs: print("\n".join(errs[:5]))
        if pages > 1:
            print("WARNING: does not fit even with the smallest margins -> shorten content "
                  "(drop the weakest project, shorter variants/summary) and rebuild")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("catalog", "build"):
        print(__doc__); sys.exit(1)
    if sys.argv[1] == "catalog":
        catalog()
    else:
        args = sys.argv[2:]
        out = "/mnt/user-data/outputs"
        if "--out" in args:
            out = args[args.index("--out") + 1]
        build(args[0], out, make_pdf="--no-pdf" not in args)
