# skills

Личные скиллы для Claude Code. Репо клонируется прямо в `~/.claude/skills`:

```bash
git clone git@github.com:kudrmax/skills.git ~/.claude/skills
```

`.gitignore` устроен как белый список: в git попадают только перечисленные в нём папки.
Всё, что кладут в `~/.claude/skills` другие инструменты (установщик `avito ai skills`,
синхронизация с claude.ai в `synced/`, симлинк `save-note` из Obsidian), игнорируется само.
Новый личный скилл — одна строка `!/<имя>/` в `.gitignore`.

Скрипты скиллов запускаются через общий venv:

```bash
python3 -m venv ~/.claude/skills/.venv && ~/.claude/skills/.venv/bin/pip install lxml markdown pypdf
```
