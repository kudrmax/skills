# skills

Личные скиллы для Claude Code. Репо клонируется прямо в `~/.claude/skills`:

```bash
git clone git@github.com:kudrmax/skills.git ~/.claude/skills
```

Любая новая папка в `~/.claude/skills` сразу видна в `git status` — личный скилл не потеряется.
В `.gitignore` только служебное (`synced/` от Claude Code, `.venv/`) и рабочие скиллы Авито по именам.
Скиллы из установщика `avito ai skills add` появляются здесь как симлинки в `~/.agents/skills`;
коммитить их не нужно, на другой машине их ставит тот же установщик.

Скрипты скиллов запускаются через общий venv:

```bash
python3 -m venv ~/.claude/skills/.venv && ~/.claude/skills/.venv/bin/pip install lxml markdown pypdf
```
