# 2. feladat
## Meg tudod nevezni a legrosszabb csoportot, annak n értékét, és össze tudod vetni a ROC AUC-jét az összesített 0.8345 értékkel.

A legrosszabb teljesítményt mutató alcsoport az `age_band` szelet `50+` csoportja: a ROC AUC mindössze **0.6071**, ami **0.2274-gyel elmarad** az összesített 0.8345-ös értéktől ($n = 19$). Ugyanebben a csoportban az FPR 0.4167 (a `21-29`-es csoport 0.0685-ös értékéhez képest +0.3482).

A kis elemszám ($n = 19$) miatt ez az eltérés nem feltétlenül jelent modellhibát; üzleti vagy fejlesztési döntés előtt több adatgyűjtés és újabb tesztelés szükséges.

# 4. feladat
# 5. feladat