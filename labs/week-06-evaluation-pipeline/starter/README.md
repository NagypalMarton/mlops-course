---
description:
  title: "6. heti labor: Értékelési folyamat"
  summary: |
    Bontsd csoportokra a teszthalmazt, pontozd mindegyiket, írd le a cukorbetegség-modell
    elfogadási feltételeit és GO/NO-GO kapuját, valamint érd el, hogy a `dvc repro`
    leálljon, a `register` pedig elutasítsa a hibás modellt. Ezután vizsgáld meg a modell
    csoportonkénti hibáit, és opcionálisan emeld a lécet egy jobb modellel.
---

# 6. heti labor: Értékelési folyamat

Az 5. héten kaput tettél az adatok elé. Egy modell ettől még nem biztos, hogy biztonságosan
kiadható. Egyetlen pontossági érték elrejti, hogy mely betegcsoportoknál téved a modell,
és senki nem írta le, mit jelent az, hogy „elég jó”.

Ma csoportokra bontod a teszthalmazt, és minden csoportot lepontozol. Leírod az elfogadási
feltételeket, valamint a GO vagy NO-GO döntést hozó kaput. Beállítod, hogy a kapu leállítsa
a `dvc repro` futását, a `register` és a `promote` pedig GO nélküli modellt utasítson el.
A végén megvizsgálod a modell csoportonkénti hibáit, és opcionálisan egy jobb modellel
emeled a lécet.

Minden gyakorlathoz háttéranyag: a 6. heti előadás és a `docs/notes/week-06-notes.md`.

## Alapul szolgáló anyagok

- **scikit-learn, model evaluation:** https://scikit-learn.org/stable/modules/model_evaluation.html
- **fairlearn, értékelési útmutató** (`MetricFrame` és a méltányossági metrikák): https://fairlearn.org/main/user_guide/assessment/perform_fairness_assessment.html
- **Google, a gépi tanulás szabályai**, a metrikákról és szeletelésről szóló 12–19. szabály: https://developers.google.com/machine-learning/guides/rules-of-ml
- **Breck és munkatársai, The ML Test Score**, a labor által megvalósított ellenőrzőlista: https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/

**Eltérések a hivatkozott anyagoktól:**

1. **Két szabály a fairlearn fölött.** A fairlearn minden csoportot összehasonlít, bármilyen
   kicsi is, és 0,0-s TPR-t jelez egy pozitív példát sem tartalmazó csoportra.
   A `fairness_report` az ilyen rátát nem definiáltként (None) jelzi, továbbá kihagyja a
   különbségek számításából az 5 sornál kisebb, illetve nem mindkét osztályt tartalmazó
   csoportokat. Így egy különbséget soha nem két beteg, illetve nem létező ráta határoz meg.
2. **A kapu DVC-szakasz, de semmi nem függ tőle.** Az 5. heti kapu azért működött, mert a
   `prepare` függött az eredményfájltól. A `gate` az utolsó szakasz, ezért a `register` és a
   `promote` helyette közvetlenül az eredményét olvassa (4. gyakorlat).
3. **A küszöbértékeket a számok megismerése után választod ki.** Egy valódi projektben a
   csapat még a futtatás előtt megállapodik bennük.

## Előfeltételek

- `uv`: https://docs.astral.sh/uv/getting-started/installation/
- Docker Desktop, vagy Docker Engine Compose bővítménnyel, legalább 24-es verzióban. A 4.
  gyakorlattól lesz rá szükséged.
- A **5500, 5510, 5511, 5532** portok legyenek szabadok.
- **Először állítsd le az 5. heti stacket.** Ugyanezeket a portokat használja:
  ```bash
  cd ../../week-05-data-validation/solution && docker compose down
  ```

---

## 1. lépés: függőségek

```bash
uv sync --all-groups
```

Újdonság ezen a héten: **`fairlearn`**, amely egyetlen hívással (`MetricFrame`) pontozza
az összes csoportot, és kiszámítja a méltányossági metrikákat.

## 2. lépés: konfiguráció

```bash
cp .env.example .env
```

Állítsd az `MLFLOW_MODEL_OWNER` értékét a nevedre. A kísérlet neve most `diabetes-week6`.

## 3. lépés: az adathalmaz

A DVC-beállítás ehhez a laborhoz tartozik: a `.dvc/config` nevezi meg a Silo távoli tárhelyet,
a `data/measurements.csv.dvc` pedig a mutató. Állítsd elő az adatokat a `data/raw/` két
batchéből, majd futtasd a folyamatot:

```bash
make data-v2
make verify-data
make repro
```

A `make verify-data` várt kimenete: `workspace matches pointer: True`. A `make repro` a
`validate`, `prepare`, `train` és `evaluate` szakaszokat futtatja, és 0.7656 pontosságot,
0.6964 precisiont, 0.5821 recallt, 0.6341 F1-et, valamint 0.8345 ROC AUC-t ír ki. Ezek az
5. hét számai: ezen a héten nem módosítjuk a modellt.

## 4. lépés: tesztek a kezdés előtt

```bash
uv run pytest tests/
```

Várt eredmény: **136 passed, 31 skipped**.

Indítsd el a Docker-stacket (az MLflow-t és a tárolóit) a `make up` paranccsal, és hagyd
futni. A 4. és 6. gyakorlathoz szükség van rá.

---

## Gyakorlatok

Sorrendben végezd el őket. A 2., 4. és 5. gyakorlat **írásos választ** kér: írd a választ
ebben a mappában az `answers.md` fájlba, és **commitold a kódoddal együtt**. A 6. gyakorlat
opcionális. Az 1–3. és az 5. gyakorlathoz nincs szükség Dockerre.

| Block | Exercises | Time |
| --- | --- | --- |
| Beállítás (1–4. lépés) | — | 10 perc |
| Szeletek | 1–2 | 25 perc |
| A kapu | 3–4 | 35 perc |
| Méltányosság | 5 | 15 perc |
| Befejezés: commit és beadás | — | 5 perc |
| Opcionális: a racsni | 6 | 15 perc |

### 1. gyakorlat: a teszthalmaz szeletelése (≈ 15 perc)

Egyetlen pontossági érték mind a 192 tesztbeteg átlaga. Annak megállapításához, hogy melyik
csoportnál téved a modell, ugyanazt a teszthalmazt csoportonként pontozod. A csapatok akkor
tesznek így, amikor a modell a műszerfalon jónak tűnik, de egy klinika, piac vagy korcsoport
panaszt tesz.

**Teendők:**

1. Olvasd el a `slice_labels` függvényt a `src/week_06_evaluation_pipeline/evaluation.py`
   fájlban. Teljes. A `params.yaml` (az `evaluation` alatt) egyik szeletdefiníciójából
   minden sorhoz csoportcímkét készít. Figyeld meg, hogy a 0 BMI-hez a `missing` címke
   tartozik, nem a legalacsonyabb sáv.
2. Ugyanebben a fájlban valósítsd meg a `group_scores` függvényt a fairlearn
   `MetricFrame` osztályával. Egy hívással pontozza egy szelet minden csoportját, és
   csoportonként egy sort tartalmazó táblázatot ad vissza. Az alatta lévő `group_metrics`
   alakítja át ezt a táblázatot JSON-rekordokká.
3. A `pipeline.py` fájlban töltsd ki a `slice_report` `evaluate`-beli hívásának argumentumait.
4. Futtasd a folyamatot, és írasd ki a táblázatot:
   ```bash
   make repro
   make slices
   ```
   Várt kimenet: a `make repro` kiírja: `10 slice group(s) across 3 axes -> metrics/slices.json`,
   a `make slices` pedig mindhárom szelethez egy táblázatot ír ki, minden sorban `n` és `pos`
   értékkel.

**Ellenőrzés:**

- Töröld az 1. gyakorlathoz tartozó kihagyásjelölőket a `tests/test_evaluation.py` fájlból.
- Futtasd a `uv run pytest tests/test_evaluation.py` parancsot.
  Várt kimenet: `16 passed`
- Futtasd a `make slices` parancsot. A kimenet első sora:
  ```text
  192 rows, 67 positive (34.9% prevalence)
  ```
  Az `50+` korosztályban `n` 19, az `under_normal` BMI-sávban pedig `n` 30 és `pos` 1.

**Elakadtál?**

- Előadás: „Szeletmetrikák a kódban” és „Melyik BMI-csoportba kerül a BMI nélküli beteg?”
- Jegyzetek: „Szeletek és elemszám” és „A nyers értékek szeletelése”
- fairlearn-dokumentáció: https://fairlearn.org/main/user_guide/assessment/perform_fairness_assessment.html
- scikit-learn-dokumentáció: a modellértékelési útmutató (fenti link)
- Ha a `missing` BMI-csoport hiányzik a táblázatból, ellenőrizd, melyik dataframe-et szeleteled.

### 2. gyakorlat: a szelettáblázat értelmezése (≈ 10 perc) *(írásos válasz)*

A táblázat két dolga nem látható az összesítő sorban. A szelettáblázat gyors értelmezésére
akkor van szükség, amikor egy felülvizsgáló megkérdezi: „mindenki számára jó?”, és öt perced van.

**Teendők:**

1. Futtasd a `make slices` parancsot. Minden sorban először az `n` és a `pos` értéket olvasd
   el, majd hasonlítsd össze a metrikákat az `aggregate` sorral.
2. Keresd meg a legalacsonyabb ROC AUC-vel rendelkező csoportot. Jegyezd fel az `n` értékét,
   és hasonlítsd össze az `fpr` értékét a `21-29` csoport `fpr` értékével.
3. Keresd meg azt a csoportot, ahol az F1 0.0000, a ROC AUC pedig 1.0000, és nézd meg a
   `pos` értékét.

**Ellenőrzés:**

- Meg tudod nevezni a legrosszabb csoportot, annak `n` értékét, és össze tudod vetni a ROC
  AUC-jét az összesített 0.8345 értékkel.

**Elakadtál?**

- Előadás: „Hány beteg alkot egy szeletet?” és „Mindig ellenőrizd, mit hagytál ki”
- Jegyzetek: „Szeletek és elemszám”
- A ROC AUC nem használja a 0.5-ös küszöbértéket, az F1 viszont igen.

**Írásos válasz** (az `answers.md` fájlban):

1. Melyik csoporton teljesít a legrosszabbul a modell, és mennyivel marad el az összesítéstől?
   A csoport `n` értékét figyelembe véve mennyire bízhatsz ebben a különbségben?
2. Mit tehetsz most ezzel a megállapítással, és mire lenne szükséged ahhoz, hogy cselekedj?
3. Egy csoportban ugyanazokon a betegeken az F1 0.0000, a ROC AUC pedig 1.0000. Hogyan
   lehet mindkettő helyes, és mit árulnak el a csoportról?

### 3. gyakorlat: az elfogadási feltételek és a kapu megírása (≈ 20 perc)

Egy kiadáshoz előre egyeztetett, Gitben tárolt válasz kell arra, hogy „kiadjuk?”. A feltételeket
a `params.yaml` fájlba, az őket alkalmazó szabályokat pedig a kódba írod. Ezt a fájlt olvassa
a felülvizsgáló, amikor megkérdezi, miért engedtük ki a modellt.

**Teendők:**

1. Futtasd a kaput, mielőtt feltételeket írnál:
   ```bash
   make gate
   ```
   Várt kimenet: az első sor:
   ```text
   GO — 10 passed, 0 failed, 1 SKIPPED (criteria v1.0.0)
   ```
   Minden szelet átmegy, beleértve a 19 beteget tartalmazó `50+`, valamint az egy pozitív
   esetet tartalmazó `under_normal` csoportot is. A feltételek nélküli kapu mindent átenged.
   2. A `params.yaml` fájlban, a `criteria_version` alatt add hozzá az `acceptance` blokkot:
      a minimumokat a `minimum`, a bajnokkal való összehasonlítást a `regression`, a
      csoportszabályokat pedig a `slice_rules` alatt. Előbb futtasd a `make slices` parancsot,
      és minden értéket a kiírt számok alapján válassz ki. Az a minimum, amelyet a mindenkit
      „nem cukorbetegnek” jósló modell is teljesít, nem valódi minimum.
   3. Olvasd el az `evaluate_gate` és a `_minimum_checks` függvényt a
      `src/week_06_evaluation_pipeline/gates.py` fájlban. Ezek teljesek. A `_minimum_checks`
      megmutatja egy ellenőrzés alakját: `id`, `status` (pass, fail vagy skipped) és `reason`.
   4. Ugyanebben a fájlban töltsd ki a `_regression_checks` TODO-ját. Ez dönti el, mikor jelent
      hibát a bajnokhoz képesti visszaesés.
   5. Ugyanebben a fájlban töltsd ki a `_slice_checks` két TODO-ját: először a támogatási
      szabályokat, amelyek kihagyják a megítéléshez túl kicsi csoportot, majd az F1-szabályokat.
   6. Futtasd újra a kaput:
   ```bash
   make gate
   ```
   Várt kimenet: az első sor:
   ```text
   GO — 10 passed, 0 failed, 4 SKIPPED (criteria v1.0.0)
   ```
   A `SKIPPED` alatt a `50+` korcsoport és az `under_normal` BMI-sáv szerepel.

   **Ellenőrzés:**

- Töröld a 3. gyakorlathoz tartozó kihagyásjelölőket a `tests/test_gates.py` fájlból.
- Futtasd a `uv run pytest tests/test_gates.py tests/test_model_gate.py` parancsot.
  Várt kimenet: `36 passed, 6 skipped`
- Ellenőrizd, hogy minden küszöbérték kiváltható: mindegyikhez nevezz meg egy modellt,
  amely megbukna rajta.

**Elakadtál?**

- Előadás: „Az elfogadási feltételek négy típusa”, „Hány beteg alkot egy szeletet?” és
  „Győződj meg róla, hogy minden szabály kiváltható”
- Jegyzetek: „Elfogadási feltételek”, „Kihagyott ellenőrzések” és
  „Győződj meg róla, hogy minden szabály kiváltható”
- Ha a fejléc 0 kihagyást mutat, ellenőrizd a `_slice_checks` `too_small` értékét.
- A `minimum.f1` megléte esetén az összesített F1 és a `min_f1` különbségénél nagyobb
  `max_f1_gap` soha nem váltható ki.

### 4. gyakorlat: a kapu szakaszként és egy valódi visszaesés (≈ 15 perc) *(írásos válasz)*

Az eredményfájl, amelyet senki nem olvas, csak egy naplóbejegyzés. Ebben a gyakorlatban a
`dvc repro` leáll NO-GO esetén, a `register` és a `promote` pedig GO nélkül elutasítja a
modellt. Egy csapatban ez különbözteti meg a kaput a javaslattól: valaki péntek este beírja,
hogy `make register`.

**Teendők:**

1. A `dvc.yaml` fájlban add hozzá a `gate` szakaszt.
2. A `registry.py` fájlban érd el, hogy a `register_best_model` és a `promote_to_staging`
   a `pipeline.py` `require_go` függvényét hívja.
3. Tedd szándékosan hibássá a modellt. A Makefile `gate-fail` célja a `train.C` értékét
   1.0-ről 0.005-re módosítja, lefuttatja a `dvc repro` parancsot, megpróbálja a
   `register` és `promote` műveleteket, majd visszaállítja a `params.yaml` fájlt:
   ```bash
   make gate-fail
   ```
   Várt kimenet: az `evaluate` 0.5243 F1-et és 0.8427 ROC AUC-t ír ki. A referencia-
   küszöbértékekkel a kapu az alábbi sorokat írja ki; a te küszöbértékeid más ellenőrzéseket
   is felsorolhatnak:
   ```text
   Running stage 'gate':
   Cannot run `gate` yet:
     NO-GO. 4 acceptance criteria failed: minimum.f1, regression.f1, slice.age_band.30-39,
     fairness.age_band.tpr_gap.
   ```
   A `models/model.pkl` továbbra is szerepel a listában, a `register` és a `promote` pedig
   egyaránt a `Refusing to release.` üzenetet írja ki.

   **Ellenőrzés:**

- Töröld a 4. gyakorlathoz tartozó kihagyásjelölőket a `tests/test_model_gate.py` fájlból.
- Futtasd a `uv run pytest tests/test_model_gate.py` parancsot.
  Várt kimenet: `18 passed, 1 skipped`
- Futtasd a `make dag` parancsot.
  Várt kimenet: a `gate` az utolsó csomópont, és egyetlen szakasz sem függ tőle.
- Elindított stack mellett futtasd a `uv run pytest tests/test_mlflow_link.py` parancsot.
  Várt kimenet: `8 passed`

**Elakadtál?**

- Előadás: „A kapu a folyamatban” és „A jelentés vizsgálata”
- Jegyzetek: „A kapu mint szakasz” és „Mérés és szabályzat”
- DVC-dokumentáció: https://doc.dvc.org/user-guide/project-structure/dvcyaml-files
- Ha a `dvc repro` nem áll le, nézd meg a `main.py gate` kilépési kódját.

**Írásos válasz** (az `answers.md` fájlban):

1. Az 5. heti kapu azért működött, mert a `prepare` függött az eredményfájltól. Miért nem
   működhet ez ennél a kapunál, és mi helyettesíti?
2. Mi történik, ha a `register` nem hívja meg a `require_go` függvényt? Ki és mikor veszi
   ezt észre?
3. `C: 0.005` mellett az F1 0.1098-cal csökkent, a ROC AUC pedig nőtt. Melyik a helyes
   válasz? Mit kell tudnod a modell használatáról, és mire kötelez az
   `acceptance.regression.primary_metric`?

### 5. gyakorlat: a csoportonkénti hibák ellenőrzése (≈ 15 perc) *(írásos válasz)*

Két csoport ugyanakkora arányban kaphat pozitív előrejelzést, miközben a kihagyott esetek
száma nagyon eltérő. Ebben a gyakorlatban az előadás három méltányossági metrikáját számítod
ki a fairlearn segítségével: **demográfiai paritás**, **egyenlő lehetőség** és
**egyenlő esélyek**. Mindegyik csoportok közötti különbség: egy ráta (kiválasztási ráta,
TPR vagy FPR) két csoport közötti legnagyobb eltérése, a 0 pedig azt jelenti, hogy minden
csoportban azonos a ráta. A kód és a `params.yaml` ezeket az eltéréseket *gap* néven
nevezi (`selection_rate_gap`, `tpr_gap`). Ezután kiválasztod, hogy mely tengelyeken mely
méltányossági metrikák legyenek a kapu részei. Ezt az ellenőrzést kéri egy etikai felülvizsgálat
vagy audit.

**Teendők:**

1. A `src/week_06_evaluation_pipeline/fairness.py` fájlban valósítsd meg a `rates_by_group`
   függvényt: minden csoport kiválasztási rátáját, TPR-jét és FPR-jét egy `MetricFrame`
   segítségével.
2. Ugyanebben a fájlban valósítsd meg a `gaps` függvényt: a méltányossági metrikákat, amelyek
   mindegyike egy fairlearn-függvénnyel számított, csoportok közötti különbség. A TODO
   megnevezi a négy kulcsot: a demográfiai paritás különbségét, az egyenlő lehetőség
   különbségét, az FPR-különbséget és az egyenlő esélyek különbségét.
3. Olvasd el a `fairness_report` függvényt ugyanebben a fájlban. Hozzáad két, a fairlearnből
   hiányzó szabályt: a mérhetetlen ráta None, és csak a legalább 5 soros, mindkét osztályt
   tartalmazó csoportok kerülnek be a különbségekbe.
4. A `gates.py` fájlban töltsd ki a `_fairness_checks` TODO-ját: mi történjen, amikor egy
   különbség túllépi a határértékét. Az `acceptance.fairness` tengelyein végigiteráló ciklus,
   minden tengely saját korlátaival, már adott.
5. Írasd ki a rátákat és a méltányossági metrikákat:
   ```bash
   make fairness
   ```
   Várt kimenet: az `age_band` esetén a kiválasztási ráta különbsége 0.3030, az egyenlő esélyek
   különbsége pedig 0.3482. Az `insulin_missing` esetén a kiválasztási ráta különbsége 0.0070,
   a TPR-különbség pedig 0.1562.
6. A `params.yaml` fájlban add hozzá az `acceptance` `fairness` blokkját: tengelyenként egy
   kulcsot, a hozzá tartozó kapuzott különbségekkel és határértékekkel. Az
   `insulin_missing` tengelyen kapuzd a kiválasztási ráta és a TPR különbségét, az
   `age_band` tengelyen pedig a TPR-különbséget lazább határértékkel. Ezután futtasd a
   `make gate` parancsot.

   **Ellenőrzés:**

- Töröld az 5. gyakorlathoz tartozó kihagyásjelölőket a `tests/test_fairness.py` és a
  `tests/test_gates.py` fájlból.
- Futtasd a `uv run pytest tests/test_fairness.py tests/test_gates.py` parancsot.
  Várt kimenet: `29 passed`
- Futtasd a `make gate` parancsot.
  Várt kimenet: a fejléc `GO — 13 passed, 0 failed, 4 SKIPPED`, és három ellenőrzés
  `fairness.` kezdetű.

**Elakadtál?**

- Előadás: „Három ráta minden csoporthoz”, „Három méltányossági metrika” és
  „Mely csoportok kapnak méltányossági kaput?”
- Jegyzetek: „Csoportméltányosság” és „Méltányossági kritérium választása”
- fairlearn-dokumentáció: https://fairlearn.org/main/user_guide/assessment/common_fairness_metrics.html
- A `rates_by_group` alakja megegyezik az 1. gyakorlatbeli `group_scores` alakjával.

**Írásos válasz** (az `answers.md` fájlban):

1. Az `age_band` kiválasztási ráta különbsége 0.30 fölött van, mégis csak a TPR-különbségét
   kapuzod. Miért védhető a nagy kiválasztási ráta különbsége?
2. Az `age_band` TPR-határértéke lazább, mint az `insulin_missing` értéke. Miért, és mi
   késztetne a szigorítására?
3. Ez az adathalmaz nem tartalmaz nemre, etnikumra, jövedelemre vagy klinikára vonatkozó
   oszlopot. Nevezz meg egy csoportot, amelyre auditálni szeretnéd a modellt, de nem tudod.
   Minek kellett volna megtörténnie, és mikor?

### 6. gyakorlat (opcionális): a léc emelése racsnival (≈ 15 perc) *(írásos válasz)*

A jelenlegi bajnokkal összehasonlító kapu csak egy irányban mozog: minden jobb modell emeli
a lécet. Egy jobb modellt teszel meg bajnoknak, szinkronizálod az alapvonalat, és látod,
ahogy az eredeti modell megbukik. Ez történik akkor, amikor valaki „csak ellenőrzésképpen”
újratanít egy modellt, és a régi már nem megy át.

Ehhez a gyakorlathoz a 4. beállítási lépés Docker-stackjének futnia kell: itt található az
MLflow követőszerver és a tárolói. A regiszter, a `champion` alias és a tanítási futások itt
élnek, ezért a `make ratchet` enélkül meghiúsul.

**Teendők:**

1. Ellenőrizd, hogy fut-e a stack. Ha leállítottad, indítsd újra:
   ```bash
   make up
   make ps
   ```
   Várt kimenet: a `make up` akkor tér vissza, amikor minden szolgáltatás egészséges, a
   `make ps` pedig a `mlflow`, `postgres` és `s3` szolgáltatásokat `Up` (`healthy`) állapotban
   listázza. Az MLflow a
   http://localhost:5500.
2. A `src/week_06_evaluation_pipeline/baseline.py` fájlban töltsd ki a
   `baseline_from_registry` TODO-ját: töltsd be a bajnokot az aliasa alapján, és a
   `score_on_test_set` segítségével pontozd a mai tesztspliten. Az alias kikeresése és a
   visszaadott rekord már adott.
3. Futtasd végig a teljes ciklust. A cél egy random forest modellt tanít, és bajnokként
   regisztrálja. Szinkronizálja a `metrics/baseline.json` fájlt, az eredeti modellt
   összeveti az új alapvonallal, majd visszaállítja a `params.yaml` és a
   `metrics/baseline.json` fájlokat. A `champion` alias a random forest modellen marad:
   ```bash
   make ratchet
   ```
   Várt kimenet: az 1. felvonás `GO` eredményt ír ki, a `regression.f1` pedig +0.0111 értékkel
   átmegy. A 3. felvonás ezt írja ki:
   `NO-GO. 1 acceptance criteria failed: regression.f1.`, majd ezt:
   `The logistic regression did not get worse. The bar got higher.`

**Ellenőrzés:**

- Töröld a 6. gyakorlathoz tartozó kihagyásjelölőt a `tests/test_model_gate.py` fájlból.
- Futtasd a `uv run pytest tests/test_model_gate.py` parancsot.
  Várt kimenet: `19 passed`
- Futtasd a `make baseline` parancsot.
  Várt kimenet: az első sor `baseline source : week-05 reference run`, az `f1` pedig
  0.6341. A racsni visszaállította a lécet.

**Elakadtál?**

- Előadás: „A léc feljebb kerül” és „Honnan származik a bajnok pontszáma?”
- Jegyzetek: „A racsni”
- MLflow-dokumentáció: https://mlflow.org/docs/latest/ml/model-registry/workflow/
- A verziót a `settings.champion_alias` alias alapján keresd ki, ne egy szám alapján.
- A tanításkor tárolt pontszám az adott nap teszthalmazához tartozik; pontozd újra a modellt.

**Írásos válasz** (az `answers.md` fájlban):

1. A racsni csak egy irányban mozog. Mondj egy helyzetet, amelyben ezt szeretnéd, és egyet,
   amelyben kizár egy modellt, amelyet ki kellett volna adnod.
2. Mit mér a bajnok pontszáma?

## Befejezés: commitold és add be a munkád (≈ 5 perc)

1. Futtasd a `uv run pytest tests/` parancsot.
   Várt kimenet: `158 passed, 9 skipped`. A 8 kihagyott teszthez kell a stack és a
   `make link`; a kilencedik a 6. gyakorlat (`159 passed, 8 skipped`, ha elvégezted).
2. Commitold a munkádat:
   ```bash
   git status          # az answers.md-nek szerepelnie kell; .env és .venv/ nem szerepelhet
   git add .
   git commit -m "week06: slices, acceptance gate, fairness checks and written answers"
   ```
3. Ellenőrizd, hogy a `params.yaml`, `dvc.yaml`, `dvc.lock`, `metrics/slices.json`,
   `reports/gate.json` és az `answers.md` szerepelnek a commitban, és **egyik alábbi sem**
   szerepel benne: `.env`, `.venv/`, `.dvc/cache/`, `data/measurements.csv`.
4. Pushold a commitot, nyisd meg GitHubon (`https://github.com/<you>/<repo>/commit/<hash>`),
   és töltsd fel az URL-t a Moodle-be.

---

## Make-célok

| Cél | Mit csinál |
| --- | --- |
| `make slices` | a csoportonkénti táblázat, minden sorban `n` és `pos` értékkel |
| `make gate` | a GO/NO-GO döntés; NO-GO esetén nem nulla kilépési kódot ad |
| `make fairness` | a három különbség tengelyenként |
| `make baseline` | a rögzített bajnok, amellyel a kapu összehasonlít |
| `make baseline-sync` | a `champion` pontozása a mai tesztspliten és újraírása (6. gyakorlat) |
| `make gate-fail` | a modell szándékos elrontása és a kapu működésének megfigyelése (4. gyakorlat) |
| `make ratchet` | egy jobb modell lesz a bajnok, a régit pedig elutasítja (6. gyakorlat) |
| `make data-gate-fail` | az 5. heti adatkapu: az adatok elrontása és a kapu megfigyelése |
| `make repro`, `make dag`, `make metrics` | a folyamat, a gráfja és a számai |
| `make register`, `make promote`, `make promote-champion`, `make trace` | a regiszter |

Az 5. hét minden célja továbbra is működik.

## Mi hol található

| Elem | Helye | Miért |
| --- | --- | --- |
| `params.yaml` | Git | az `evaluation` a mérés, az `acceptance` pedig az átmenés feltétele |
| `metrics/slices.json`, `reports/gate.json` | Git | `cache: false`, ezért a bizonyíték és az állítás ugyanabban a commitban van |
| `metrics/baseline.json` | Git | a rögzített bajnok; csak a `make baseline-sync` írja |
| `src/.../gates.py` | Git | tiszta függvény: egyszerű dict a bemenet, eredmény a kimenet |
| `data/measurements.csv` | Silo (`dvc-storage`) | a verziózott adathalmaz; a Gitben a mutatója van |
| `models/model.pkl`, `data/processed/*.csv` | DVC-gyorsítótár | a folyamat által újraépíthető kimenetek |

## Leállítás

```bash
make down      # leállítás; az adatok és a futások a kötetekben maradnak
make down-v    # leállítás ÉS mindkét bucket és az adatbázis törlése
```

## Hibaelhárítás

| Probléma | Megoldás |
| --- | --- |
| `Cannot run gate yet: metrics.json is missing` | Az `evaluate` még nem futott le. Futtasd a `make repro` parancsot. |
| `The gate is not implemented yet, so nothing was checked` | A 3. gyakorlat nincs kész. A parancs 1-gyel lép ki, ezért a `dvc repro` leáll. |
| `No slice report — evaluation.slice_report returns nothing yet` | Az 1. gyakorlat nincs kész. |
| `Cannot run register: reports/gate.json is missing` | A kapu még nem futott le ehhez a modellhez. Futtasd a `make repro` vagy `make gate` parancsot. |
| `The recorded verdict is NO-GO ... Refusing to release` | A kapu végzi a dolgát. Olvasd el a `reports/gate.json` fájlt, és javítsd a modellt. Küszöb módosításakor növeld a `criteria_version` értékét. |
| `register` says `No MLflow run recorded yet` | A stack le volt állítva, amikor a `train` futott. Indítsd el, majd futtasd a `make link` parancsot. |
| `ModuleNotFoundError: No module named 'fairlearn'` | Futtasd újra a `uv sync --all-groups` parancsot: a `fairlearn` ezen a héten új függőség. |
| `dvc repro` says "up to date" after you edit a threshold | Megjegyzést módosítottál, nem értéket. Ellenőrizd a `dvc params diff` kimenetét. |
| `Bind for 0.0.0.0:5500 failed: port is already allocated` | Egy másik hét stackje fut. Állítsd le a mappájában a `docker compose down` paranccsal. |

## Következő lépések

A folyamatnak most mindkét végén van kapuja. A kapu csak akkor fut, amikor valaki elindítja:
semmi nem akadályozza meg a csapattagot a `make gate` kihagyásában, vagy egy azt elrontó
módosítás összeolvasztásában. A 7. héten a folyamatos integráció minden commitnál automatikusan
lefuttatja ezeket az ellenőrzéseket.
