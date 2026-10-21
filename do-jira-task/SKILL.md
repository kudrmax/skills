---
name: do-jira-task
description: Выполнить задачу из Jira по ссылке или номеру (FMP-NNNNN) до драфт-PR. Триггеры — «/do-jira-task FMP-12345», «сделай задачу <ссылка на jira>».
argument-hint: <ссылка или номер задачи>
---

Выполни задачу $ARGUMENTS (прочитай её через MCP jira).

- Сначала подтяни актуальный master (`git pull --ff-only` в основном клоне).
- Работай в отдельном worktree от master, ветка `FMP-NNNNN-something`.
- Перед коммитом прогони `avito fmt` и `avito lint`.
- Результат: драфт PR(ы).
