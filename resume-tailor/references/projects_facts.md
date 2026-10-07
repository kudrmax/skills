# Факты из README пет-проектов (снимок октября 2026)

Источник правды для новых формулировок. Не выдумывай цифры и инструменты, которых здесь нет.
Читай только секцию нужного проекта: `grep -A25 "^## <id>" projects_facts.md`.

## bank — classic-ML-models-in-Bank-Marketing (соло, апрель 2026)
- UCI Bank Marketing, bank.csv: 4521 строк, 16 признаков, таргет «откроет ли вклад»; дисбаланс 4000:521 (~8:1).
- Удалён `duration` как data leakage. Признаки: ordinal education + флаг education_is_known, sin/cos месяца, cbrt(balance), флаг was_contacted (pdays=-1).
- Pipeline + ColumnTransformer (StandardScaler, OneHotEncoder handle_unknown='ignore').
- Метрики: PR-AUC и F2 (важен recall). Модели и PR-AUC: KNN 0.30, CART 0.32, LinearSVC L2/L1 0.40, LogReg 0.40, GradBoost 0.43, RF(d=5) 0.46, CatBoost 0.47.
- Выводы: балансировка поднимает F2 (0.19→0.42), не меняя PR-AUC (сдвигает порог); L1 зануляет мелкие веса; RF не переобучается по n_estimators, оптимум глубины 5; GB переобучается после ~25 деревьев; KNN страдает от OHE (проклятие размерности); CatBoost с ordered target encoding без прироста.
- Стек: pandas, scikit-learn, catboost, numpy, matplotlib, seaborn.

## samokat — kudrmax/samokat-search-ml (КОМАНДНЫЙ, июль 2026; репо коллеги)
- E-commerce поиск Самоката. ~80K (79,774) пар запрос–товар, 9,496 уникальных запросов, разметка ESCI (E 45.7%, I 36.6%, S 11.7%, C 6.1%).
- EDA запросов (1–2 слова, биграммы, wordcloud); иерархия категорий (anytree, networkx).
- Классификатор категорий запроса: эмбеддинги e5-small-en-ru + каскад kNN cat1→cat2. Accuracy cat1 90.4% (macro F1 0.846), cat2|cat1 95.2%, полный путь 86.1%.
- Опечатки: 48% запросов с опечатками, 9 типов. SymSpell+словарь 53.4%, SymSpell+MARISA-префиксы+pymorphy3 75.3%, seq2seq sage-fred5 34.2%. Кластеризация запросов e5+UMAP+HDBSCAN.
- ESCI-релевантность: признаки word_overlap, SequenceMatcher, TF-IDF cos, e5 cos; сравнение LinearSVC/LogReg/RF/GradBoost (ROC-AUC, время инференса); итог — двухэтапный GradBoost (I vs не-I, затем C/S/E): accuracy 0.69, macro F1 0.505.
- Графы заменителей (42,183 рёбер) и комплементов (18,550) в NetworkX + Plotly.
- Личный вклад пользователя внутри команды не уточнён — формулировать «в команде».

## liza — LizaAlert (КОМАНДНЫЙ, июль 2025)
- Датасет о пропавших людях от лаборатории «Искусство и ИИ»: сильно зашумлён, большинство полей только в свободном тексте `content`.
- Очистка: дубликаты, нормализация пола/статуса, разбор возраста, даты на компоненты, search_period, заполнение пропусков; пол по имени через pymorphy3; NLTK; карта folium.
- EDA: пики возраста 12–17, 32–42, 68–75; сезонный пик летом; география повторяет плотность населения.
- Модели: LogReg, KNN, Decision Tree, Random Forest.
- ВНИМАНИЕ: таблица метрик в README (RF 0.87 и т.п.) помечена в самом README как «придуманные» — НИКОГДА не использовать эти цифры.

## yolo — YOLOv8_detecting_hardhats-and-vests (соло, июнь 2026)
- Roboflow Hardhat dataset, 2 класса, 416×416, сплит 1502/429/215.
- EDA: баланс классов, пропорции bbox (каски горизонтальные, жилеты вертикальные), смещение центров к центру кадра, до 33 объектов на кадр.
- YOLOv8s (11.1M параметров), transfer learning с COCO (перенесено 349/355 слоёв), 50 эпох, Tesla T4 ~15 мин, AdamW, mosaic первые 40 эпох.
- Метрики (val): P 0.922, R 0.863, mAP50 0.925, mAP50-95 0.709; vest 0.948 vs hardhat 0.903. Межклассовых ошибок нет.
- Анализ confidence: двугорбое распределение, гиперболическая зависимость от площади объекта (<0.025 — неуверенно).

## onepiece — OnePieceClassifier-CW (соло, курсовая, май 2025)
- 18 классов, 3705→6298 изображений после аугментаций, 224×224. Своя CNN на PyTorch (3 conv + 2 fc, 22M параметров), Dropout, L2, LR-scheduler.
- Исследование BatchNorm (стабилизирует градиенты, замедляет переобучение), нормы градиентов по слоям, SoftMax vs SparseMax.
- Accuracy ~0.67 — слабая, не упоминать цифру.

## kmeans — KMeans-DBSCAN (соло)
- K-Means на Wine (178×13), нормализация [0,1], 15 запусков: средняя точность 0.947, 4–11 итераций.
- DBSCAN на Aniso (800 точек): сетка ε 0.1–0.75 × m 1–25 (200 комбинаций), лучшее ε=0.38, m=4 → 99.12%.
- Алгоритмы реализованы в репозитории (папки KMeans/, DBSCAN/).

## titanic — titanic-RandomForest (соло, май 2026)
- OpenML Titanic 1309×14. Удалены boat/body (leakage), cabin (77% пропусков). Признаки is_cabin, is_alone, log(fare).
- Pipeline (SimpleImputer + OHE) + RandomForest (130 деревьев, depth 20, leaf 2, balanced); подбор по сетке с кривыми. Accuracy test 0.8092.

## mpi — MPI_N_bodies (соло, C++, март 2024)
- Гравитационная задача N тел, метод Рунге–Кутты 4-го порядка, распараллеливание MPI, анимации траекторий.
- Замеры: до 200K тел, 4/8/16/54 процесса; ускорение ~3.9× (4), ~7.6× (8), ~14.6× (16), до 37.8× (54 процесса, 20K тел).

## space — Space-Invaders-Pygame (соло, Python)
- Игра на PyGame: пушка, пришельцы с разными типами (бонус hp, ускорение стрельбы), НЛО с неуязвимостью, рекорд, прогресс-бары эффектов; все параметры вынесены в CONSTANTS.py.
