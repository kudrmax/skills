# Cover / motivation letters

Read this file ONLY when the user explicitly asks for «сопроводительное», «мотивационное», «cover letter»,
«motivation letter» or similar. Never write a letter on your own initiative.

## Source of facts
- The letter must describe exactly the same person as the resume built in this chat: same title, same
  projects, same stack. Take facts from `/tmp/selection.json` (or the last resume reply) plus the vacancy.
  If no resume was built yet in this chat, build it first (normal workflow), then write the letter.
- Allowed facts: CROC (full-time BI/DWH Analyst, Sep–Dec 2025: OLAP cubes, SQL/PostgreSQL on multi-million-row
  samples, ETL and data-prep automation, BI dashboards), Python, projects from `projects_facts.md`,
  courses (ШАД «Продвинутое машинное обучение», ФКН ВШЭ «Машинное обучение» — completed, DLS МФТИ),
  familiarity with NoSQL. No Alpha-Bank, no other employers, nothing not in the resume data.

## Two types
- **Сопроводительное / cover letter (default):** cold, short, 80–150 words, 3–5 short paragraphs.
- **Мотивационное / motivation letter, or user says "длинное", or an internship with a selection process:**
  250–400 words; add a list "требование вакансии → мой опыт" (3–5 points, each 1–2 sentences) and a
  paragraph on why this domain/company.

## Structure (in this order)
1. Greeting. RU: «<Имя рекрутера>, добрый день!» if the vacancy names a recruiter, else
   «Представитель компании <Компания>, добрый день!». EN: «Dear <Name>,» or «Dear <Company> team,».
2. RU only, verbatim: «Меня зовут ИМЯ ФАМИЛИЯ, окончил МГТУ им. Баумана по направлению "Прикладная
   математика" и магистратуру "Искусственный интеллект" МЭИ.» EN: never mention the name; education as
   «I hold a B.Sc. in Applied Mathematics from Bauman Moscow State Technical University and an M.Sc. in
   Artificial Intelligence from MPEI.»
3. Position and why I apply — one sentence tied to the vacancy's essence.
4. 2–3 concrete facts from experience that match the vacancy requirements (numbers where they exist).
   Mention 2 most relevant projects by name with «(см. резюме)» / «(see CV)» — no links.
5. Why this company: 1–2 specifics from the vacancy (product, stack, domain, team).
   For RecSys, classical ML or Computer Vision roles add that I want to build my career specifically in
   this ML domain.
6. Key gaps only (1–2 must-haves I lack): «<X> не использовал в работе, готов освоить» / «ready to learn <X>».
   Courses only if relevant to the role.
7. Format: Russian employer → «Рассматриваю удалённый формат работы.» Serbian employer or job in Serbia →
   «Готов к релокации в Белград и выходу на работу в любое время.» / «I am ready to relocate to Belgrade
   and start at any time.» Other → nothing.
8. Short close: «Буду рад обсудить детали.» / «I would be glad to discuss the role.»
9. Ending, verbatim, separated by an empty line:
   RU:
   ```
   Резюме: ❗️❗️❗️❗️❗️❗️❗️ВСТАВИТЬ❗️❗️❗️❗️❗️❗️❗️
   GitHub: https://github.com/GITHUB_USER?tab=repositories
   ```
   EN:
   ```
   CV: ❗️❗️❗️❗️❗️❗️❗️ВСТАВИТЬ❗️❗️❗️❗️❗️❗️❗️
   GitHub: https://github.com/GITHUB_USER?tab=repositories
   ```
   No signature block before it.

## Tone and don'ts
Cold, matter-of-fact, but clearly interested in this specific role. Avoid: retelling the whole resume;
unproven qualities («ответственный», «быстро учусь»); emotional or exalted phrasing («мечтаю», «без лукавства»,
«страсть», «thrilled», «passionate»); clichés («динамично развивающаяся компания»); skills not in the resume;
apologies for little experience; salary; emoji other than the ❗️ marker; personal details.
Language = vacancy language (Serbian vacancies in English → English).

## Output
The letter as plain text inside one triple-backtick block, nothing else inside it. Outside the block at most
one line (e.g. which gap was mentioned). Do not regenerate the resume when only the letter is asked.

## Example (short, RU, approved style)
```
Представитель компании InfoVizion, добрый день!

Меня зовут ИМЯ ФАМИЛИЯ, окончил МГТУ им. Баумана по направлению "Прикладная математика" и магистратуру "Искусственный интеллект" МЭИ.

Меня заинтересовала позиция Junior BI Developer: в КРОК я работал BI/DWH-аналитиком — разрабатывал OLAP-кубы, писал SQL-запросы в PostgreSQL для выборок в несколько миллионов записей, участвовал в разработке ETL-процессов и создавал BI-дашборды. Python использую для обработки данных и автоматизации (см. резюме: «Модели классификации для банковского маркетинга», «NLP-анализ сообщений о пропавших людях»).

В вакансии привлекает сочетание Python, SQL, ETL и BI и работа с реальными объёмами данных. ClickHouse в работе не использовал, готов освоить. Рассматриваю удалённый формат работы.

Буду рад обсудить детали.

Резюме: ❗️❗️❗️❗️❗️❗️❗️ВСТАВИТЬ❗️❗️❗️❗️❗️❗️❗️
GitHub: https://github.com/GITHUB_USER?tab=repositories
```
