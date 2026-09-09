A random seed érték 42-ről 7-re történő megváltoztatása módosította a képzési és tesztelési adathalmazak felosztását, így a modellt a betegek különböző alcsoportjain képezték ki és értékelték. Ez jelentősen megváltoztatta a mért mutatókat, ami megnehezítette az eredmények reprodukálását és összehasonlítását, és potenciálisan oda vezethetett, hogy a csapat egy megbízhatatlan értékelésen alapuló modellt bocsátott ki.

## Tuned random forest

With `PIPELINE_RANDOM_SEED=42` and the existing 75/25 split, the best tested configuration was:

- `n_estimators=100`
- `max_depth=None`
- `min_samples_leaf=2`
- `class_weight="balanced"`
- `random_state=42`

The resulting test metrics were accuracy `0.7604`, precision `0.6329`, recall `0.7463`, and F1 `0.6849`. The previous default random forest scored F1 `0.6066`. Recording the parameters and seed matters because otherwise the leaderboard number cannot be reliably tied to a particular run.

A `week_01_env_setup.config` modulban történő korai ellenőrzés azért jobb, mert egyértelmű konfigurációs hibát jelez még a `train_test_split` meghívása előtt, így a hiba gyorsabban és könnyebben javítható.
