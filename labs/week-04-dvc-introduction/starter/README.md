---
description:
  title: "4. hét labor: DVC bemutatása"
  summary: |
    Helyezd a tanítóadatokat verziókezelés alá a DVC-vel, a 2./3. heti
    Silo-t S3-távoli tárhelyként használva. Kövesd az adathalmazt a tartalmi
    hash alapján, töltsd fel a bájtokat, mozogj a verziók között, deklaráld a
    folyamatot gráfként a dvc.yaml segítségével, és írd az adatverziót az
    MLflow-futtatásra, hogy a nyomonkövethetőségi lánc végül a bájtokig érjen.
---

# 4. hét labor: DVC bemutatása

Az előző heti nyomonkövethetőségi lánc egy telepített aliastól visszavezetett egy futtatáshoz és annak git-
commitjához, majd a `data/diabetes.csv` fájlnál állt meg: ez csak egy **útvonal**.

Ma identitást adsz az adatoknak. Az adathalmazt a tartalmi hash alapján követed, a
bájtokat pedig a Silóban tárolod. Az új kötegeket új verziókként adod hozzá, mozogsz
köztük, és deklarálod a folyamatot a `dvc.yaml` fájlban. Ezután rögzíted az adatverziót
az MLflow-futtatáson, és leállítod azt a futtatást, amelyik hibás verziót rögzítene.

Minden gyakorlathoz háttéranyag: a 4. heti előadás és a `docs/notes/week-04-notes.md`.

## Alapul szolgáló anyagok

- **DVC Get Started:** https://doc.dvc.org/start
- **S3-kompatibilis távoli tárhelyek (Silohoz):** https://doc.dvc.org/user-guide/data-management/remote-storage/amazon-s3
- **`dvc.yaml`:** https://doc.dvc.org/user-guide/project-structure/dvcyaml-files
- **Parancsreferencia:** https://doc.dvc.org/command-reference
- **MLflow-adathalmazok:** https://mlflow.org/docs/latest/ml/dataset/

**Eltérések az útmutatótól:**

1. **`dvc init --subdir`**, mert ez a labor egy nagyobb Git-tároló almappája.
2. **Silo-távoli tárhely**, nem helyi mappa, mert éppen azt a problémát oldjuk meg,
   hogy „az adatok a laptopomon vannak”.
3. **Kulcsok a környezetből**, nem a `dvc remote modify --local` használatával. A Silo
   kulcsait a terminálban exportálod a `.env` fájlból (a Makefile is ezt teszi), így
   egyetlen kulcs sem kerül konfigurációs fájlba.
4. **`core.autostage true`**, így egy `.dvc` fájl elfelejtett `git add` művelete nem
   veszíthet el adatverziót.
5. **A Pima diabétesz kötegei**, a kurzus folyamatos példája.

## Előfeltételek

- Docker Desktop vagy Docker Engine Compose pluginnal, 24-es vagy újabb verzió
- `uv`: https://docs.astral.sh/uv/getting-started/installation/
- A **5500, 5510, 5511, 5532** portok legyenek szabadok
- **Először állítsd le a 3. heti stacket.** Ugyanezeket a portokat használja:
  ```bash
  cd ../../week-03-mlflow-integration/starter && docker compose down
  ```

---

## 1. lépés: függőségek

```bash
uv sync --all-groups
```

Újdonság ezen a héten: **`dvc[s3]`**. A `boto3` és a `matplotlib` már nem szükséges.

## 2. lépés: konfiguráció

```bash
cp .env.example .env
```

Állítsd az `MLFLOW_MODEL_OWNER` értékét a nevedre. A `DVC_BUCKET` egy **második** Silo
vödröt nevez meg az adatok számára.

`PIPELINE_RANDOM_SEED`, `PIPELINE_TEST_SIZE` és `PIPELINE_MAX_ITER` a követés érdekében
a `params.yaml` fájlba kerültek.

## 3. lépés: tesztelés a kezdés előtt

```bash
uv run pytest tests/ -v
```

Várt eredmény: **26 sikeres, 25 kihagyott**. Minden kihagyás megnevezi a gyakorlatot,
amelyik feloldja.

## 4. lépés: a stack indítása

```bash
make up #docker compose up -d --wait
```

Nyisd meg a Silo konzolját a http://localhost:5511 címen. **Két** vödröt kell látnod:
`mlflow-artifacts` és `dvc-storage`.

---

## Gyakorlatok

Végezd el őket sorrendben. A 2., 4., 5. és 6. gyakorlat **írásos választ** kér (és a
7. gyakorlat is, ha elvégzed): írd a választ ebben a mappában az `answers.md` fájlba,
és **commitold a kódoddal együtt**. A 7. gyakorlat opcionális.

| Blokk | Gyakorlatok | Idő |
| --- | --- | --- |
| Beállítás (1–4. lépés) | — | 10 perc |
| Az adatok verziózása | 1–3 | 25 perc |
| Új kötegek | 4 | 15 perc |
| A folyamat | 5 | 15 perc |
| Kapcsolás az MLflow-hoz | 6 | 15 perc |
| Befejezés: commit és beadás | — | 5 perc |
| Opcionális: még nem hozzáadott adatok | 7 | 10 perc |

### 1. gyakorlat: a DVC inicializálása és a Silóra irányítása (≈ 5 perc)

DVC-nek szüksége van egy projektre és egy **távoli tárhelyre**: itt tárolja az adatokat.
Ebben az esetben a távoli tárhely a Silóban található `dvc-storage` vödör. A távoli
tárhelyet a Gitbe commitolt `.dvc/config` fájlba írja. Ezt tárolónként egyszer állítod
be, és minden új projektnél ellenőrzöd, amelyhez csatlakozol.

**Teendők:**

1. Olvasd el a Makefile `dvc-init` célját: hat parancsból áll. Itt szükség van a
   `--subdir` kapcsolóra; az `endpointurl` irányítja az „S3” távoli tárhelyet a Silóra.
2. Futtasd: `make dvc-init`
3. Nézd meg, mi jött létre, majd commitold:
   ```bash
   cat .dvc/config          # the remote, and no keys
   cat .dvc/.gitignore
   git add .dvc/config      # dvc init staged it before the remote was added
   git status               # .dvc/config, .dvc/.gitignore and .dvcignore are staged
   git commit -m "week04: initialise DVC with Silo as the remote"
   ```

**Ellenőrzés:** a munkád ellenőrzéséhez futtasd a `uv run pytest tests/test_dvc_repo.py`
parancsot. Ezt írja ki: `4 passed, 6 skipped`.
A `.dvc/config` a távoli tárhelyet `storage` néven nevezi meg, és nem tartalmaz kulcsot
vagy jelszót.

**Elakadtál?**
1. Előadás: „A DVC telepítése és projekt indítása” · Jegyzetek: „A DVC és a `dvc init` telepítése”
2. DVC-dokumentáció: https://doc.dvc.org/command-reference/init és
   https://doc.dvc.org/command-reference/remote/add
3. A „Not tracked by any supported SCM tool” azt jelenti, hogy a `dvc init` a `--subdir`
   kapcsoló nélkül futott.

### 2. gyakorlat: hozzáadás, a pointer olvasása és feltöltés (≈ 15 perc) *(írásos válasz)*

Egy klinika kötegenként, egyszerre egy CSV-fájlban küldi a méréseit. A kötegek a
`data/incoming/` mappában várakoznak. Amikor egy köteg megérkezik, a `data/raw/` mappába
másoljuk, amelyet commitolunk a Gitbe. A tanítóadat egyetlen fájl, a
`data/measurements.csv`: a `data/raw/` összes kötege egyesítve. Ezt a fájlt követi a
DVC. Minden új köteg érkezésekor újra felépíted a fájlt, a DVC pedig új verziót rögzít.

Ebben a gyakorlatban megérkezik az első köteg, és 1. verzióként rögzíted (461 sor).
Az adatok a Silóba, egy kis pointerfájl pedig a Gitbe kerül. Így oszthatsz meg egy
adathalmazt a csapattársaddal anélkül, hogy CSV-t küldenél e-mailben.

A használt kód:

- `src/week_04_dvc_introduction/cli.py` futtatja a labor minden parancsát
  (`uv run python src/main.py <command>`), és a Makefile-célok ezt hívják. Nem kell
  módosítanod.
- A `make next-batch` a következő köteget a `data/incoming/` mappából a `data/raw/`
  mappába másolja.
- A `make build-data` a `src/week_04_dvc_introduction/datasets.py` fájlban található
  `build_measurements` függvényt hívja. Ezt a függvényt neked kell megírnod.

**Teendők:**

1. Megérkezik az első köteg: a `make next-batch` ezt írja ki: `batch_01.csv arrived: 461 rows`.
2. Implementáld a `build_measurements` függvényt a `src/week_04_dvc_introduction/datasets.py`
   fájlban.
3. Építsd fel az adathalmazt: `make build-data`. A parancs kiírja a 461 sort és az md5-öt.
4. Add át ennek a terminálnak a `.env` fájlban lévő Silo-kulcsokat. A `dvc push` és a
   `dvc pull` használja ezeket. Minden új terminálban egyszer futtasd:
   ```bash
   set -a && . ./.env && set +a
   export AWS_ACCESS_KEY_ID="$S3_ACCESS_KEY" AWS_SECRET_ACCESS_KEY="$S3_SECRET_KEY"
   ```
5. Kövesd, commitold és töltsd fel az 1. verziót:
   ```bash
   uv run dvc add data/measurements.csv
   git add data/raw
   git status               # the pointer, data/.gitignore and data/raw/batch_01.csv are staged
   git commit -m "week04: dataset version 1 (batch_01)"
   uv run dvc push          # 1 file pushed
   ```
6. Nézz meg három dolgot:
   - `data/measurements.csv.dvc`: a pointer (`md5`, `size`, `hash`, `path`);
   - `data/.gitignore`: ezt a DVC írta, így a Git figyelmen kívül hagyja az adatfájlt;
   - a Silo konzolját: a `dvc-storage` vödörben nyisd meg a `dvcstore/files/md5/`
     mappát, majd az md5-ed **első két karakteréről** elnevezett almappát.

**Ellenőrzés:** a munkád ellenőrzéséhez töröld a 2. gyakorlat kihagyási jelölőit a
`tests/test_datasets.py` fájlból, majd futtasd a `uv run pytest tests/test_datasets.py`
parancsot. Ezt írja ki: `6 passed, 2 skipped`. A pointerben lévő md5:
`786c54f2770fa1e7ea5438e6e44b6486`.

**Elakadtál?**
1. Előadás: „A `dvc add` pointerfájlt ír” · Jegyzetek: „DVC: pointerek a Gitben, adatok a Silóban”
   és „Bájtpontos hash-elés és sorvégződések”
2. pandas-dokumentáció: https://pandas.pydata.org/docs/reference/api/pandas.concat.html és
   https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
3. Az eltérő md5 általában sorvégződést vagy a fájlban lévő pandas-indexoszlopot jelent.

**Írásos válasz** (az `answers.md` fájlban):

1. Mit kapott a Git ebben a commitban, és körülbelül hány bájtot? Mit kapott a Silo?
   Miért ez a különbség a DVC lényege?
2. Egy csoporttárs ugyanazzal a köteggel futtatja a `make build-data` parancsot, és
   bájtpontosam azonos `.dvc` fájlt kap. Nevezz meg két dolgot, amit a
   `build_measurements` ennek érdekében tesz, és egyet, ami ezt megtörné.
3. Egy csapattárs klónozza a tárolót. Megvan neki a `data/measurements.csv.dvc`, de nincs
   `data/measurements.csv`. Melyik egyetlen parancsot futtatja, és melyik két feltételnek
   kell teljesülnie ahhoz, hogy működjön?

### 3. gyakorlat: a teljes oda-vissza út bizonyítása (≈ 5 perc)

A DVC kétféleképpen tudja visszaállítani az adatokat. A `dvc checkout` a helyi gyorsítótárból
állítja vissza, a `dvc pull` pedig először letölti a távoli tárhelyről. Ismerned kell a
különbséget, amikor egy véletlenül törölt fájlt állítasz vissza, illetve amikor egy új
csapattárs klónozza a tárolót.

**Teendő:** töröld az adatfájlt **és** a gyorsítótárat, majd próbáld visszaszerezni az adatokat:

```bash
rm data/measurements.csv
rm -rf .dvc/cache
uv run dvc checkout data/measurements.csv   # fails: the bytes are not in the cache
uv run dvc pull data/measurements.csv       # downloads them from Silo
uv run python src/main.py verify-data       # compares the file with its pointer
```

Name the file in each command. Without it, DVC also tries to restore other outputs.
`make dvc-roundtrip` runs the same steps.

**Ellenőrzés:** a `dvc checkout` a `Checkout failed for following targets` üzenettel
végződik, a `dvc pull` kiírja, hogy `1 file fetched and 1 file added`, a `verify-data`
pedig ezt írja ki: `workspace matches pointer: True`.

**Elakadtál?**
1. Előadás: „`dvc checkout`: visszaállítás a gyorsítótárból” és „`dvc pull`: adatok letöltése” ·
   Jegyzetek: „`checkout` és `pull`”.
2. DVC-dokumentáció: https://doc.dvc.org/command-reference/checkout és
   https://doc.dvc.org/command-reference/pull
3. Az `Unable to locate credentials` azt jelenti, hogy ennek a terminálnak nincsenek kulcsai:
   ismételd meg a 2. gyakorlat 4. lépését.

### 4. gyakorlat: új kötegek és időutazás (≈ 15 perc) *(írásos válasz)*

Megérkezik még két köteg, így az adathalmaz 2. és 3. verziót kap. Ezután visszamész az
1. verzióhoz, majd ismét előrelépsz. „Milyen adatokat látott a múlt havi modell?” – ezt a
kérdést a munkád során is fel fogják tenni, és így tudsz rá válaszolni.

**Teendők:**

1. Megérkezik a második köteg. Építsd fel, kövesd, commitold és töltsd fel a 2. verziót:
   ```bash
   make next-batch                                 # batch_02.csv arrived: 107 rows
   make build-data                                 # 568 rows
   uv run dvc status data/measurements.csv.dvc     # modified: data/measurements.csv
   uv run dvc add data/measurements.csv
   git add data/raw
   git commit -m "week04: dataset version 2 (batch_02)"
   uv run dvc push
   ```
2. Megérkezik a harmadik köteg: ismételd meg az 1. lépést a 3. verzióhoz
   (`batch_03.csv`, 768 sor).
3. Keresd meg az 1. verzió commitját: a `git log --oneline -- data/measurements.csv.dvc`
   három commitot listáz, legfelül a 3. verzióval. Másold ki az 1. verzió hashét.
   Hasonlítsd össze a verziókat, térj vissza az 1. verzióhoz, majd lépj előre ismét:
   ```bash
   uv run dvc diff --targets data/measurements.csv -- <version 1 commit>
   git checkout <version 1 commit> -- data/measurements.csv.dvc
   uv run dvc checkout data/measurements.csv
   uv run python src/main.py verify-data           # 461 rows
   git checkout HEAD -- data/measurements.csv.dvc
   uv run dvc checkout data/measurements.csv       # 768 rows again
   ```
   A `make dvc-timetravel REV=<version 1 commit>` ugyanilyen időutazást hajt végre.

**Ellenőrzés:** a munkád ellenőrzéséhez töröld a 4. gyakorlat kihagyási jelölőit a
`tests/test_datasets.py` fájlból, majd futtasd a `uv run pytest tests/test_datasets.py`
parancsot. Ezt írja ki: `8 passed`. A 2. verzió md5-e `66f7...`, a 3. verzióé pedig
`a8fd...`.

**Elakadtál?**
1. Előadás: „Visszatérés az 1. verzióhoz” · Jegyzetek: „Visszatérés egy korábbi verzióhoz”.
2. DVC-dokumentáció: https://doc.dvc.org/command-reference/diff és
   https://doc.dvc.org/command-reference/checkout
3. A `pathspec ... did not match` azt jelenti, hogy abban a commitban nincs pointer.
   Használd a `git log --oneline -- data/measurements.csv.dvc` által listázott 1. verziós commitot.

**Írásos válasz** (az `answers.md` fájlban):

1. Az időutazás **két** parancsot igényelt. Mit változtatott a lemezen a `git checkout`,
   mit változtatott a `dvc checkout`, és miért nem tudja egyik sem elvégezni a másik feladatát?
2. Ugyanezt az időutazást egy olyan laptopon próbálod végrehajtani, amely soha nem töltötte
   le az 1. verziót. Mi történik?

### 5. gyakorlat: a folyamat deklarálása (≈ 15 perc) *(írásos válasz)*

A folyamat három szakaszból áll: `prepare → train → evaluate`. A szakaszokat a
`dvc.yaml` fájlban deklarálod, így a DVC tudja, hogy az egyes szakaszok mit olvasnak és
írnak, és csak azt futtatja újra, amire a változás hatással van. A deklarált folyamat
lehetővé teszi, hogy egy csapattárs vagy a CI újraépítse a modelledet anélkül, hogy
meg kellene kérdeznie, hogyan tegye.

**Teendők:**

1. A `dvc.yaml` fájlban add hozzá a `train` és `evaluate` szakaszt. Olvasd el a
   `pipeline.py` fájlban a `train()` és `evaluate()` függvényt, és sorolj fel minden
   fájlt, amelyet az egyes szakaszok olvasnak (adatot és forráskódot), minden általuk
   használt paramétert, valamint minden általuk írt fájlt.
2. Futtasd a folyamatot kétszer:
   ```bash
   make repro      # runs every stage
   make repro      # runs nothing: "didn't change, skipping"
   make dag
   make metrics
   ```
3. Módosítsd a `params.yaml` fájlban a `train.C` értékét `1.0`-ről `0.1`-re, futtasd
   újra a `make repro` parancsot, majd:
   ```bash
   uv run dvc params diff
   uv run dvc metrics diff
   ```
   Állítsd vissza a `train.C` értékét `1.0`-re, és futtasd a `make repro` parancsot.
4. Nyisd meg és olvasd el a `dvc.lock` fájlt.

**Ellenőrzés:** a munkád ellenőrzéséhez töröld a kihagyási jelölőket a
`tests/test_dvc_yaml.py` fájlból, majd futtasd a `uv run pytest tests/test_dvc_yaml.py`
parancsot. Ezt írja ki: `3 passed`. A `C` módosítása után a `prepare` kimarad, a
`train` és az `evaluate` pedig lefut. A `make dag` négy csomópontot jelenít meg.

**Elakadtál?**
1. Előadás: „Folyamatszakaszok” és „a `dvc repro` olyan, mint a `make`” · Jegyzetek: „A folyamat”
2. DVC-dokumentáció: `dvc.yaml` fájlok (a fenti hivatkozáson)
3. Ha az `evaluate` nem fut újra a `train` után, ellenőrizd, hogy minden általa olvasott
   fájl szerepel-e a `deps` között.

**Írásos válasz** (az `answers.md` fájlban):

1. Sorold fel az `evaluate` szakaszod `deps` értékeit. Válassz ki egyet, és mondd el,
   mi történik, ha kimarad a listából. A folyamat meghiúsul, vagy lefut és hibás eredményt ad?
2. A 3. verzióban ugyanaz a 768 sor található, mint a `data/diabetes.csv` fájlban.
   Hasonlítsd össze a `make metrics` eredményét a kurzus rögzített alapértékével
   (accuracy 0.7344, F1 0.5785). Eltérnek. Magyarázd meg, hogy „ugyanazok a sorok”
   miért nem jelentik azt, hogy „ugyanaz az adathalmaz”.

### 6. gyakorlat: a futtatás és az adatverzió összekapcsolása (≈ 15 perc) *(írásos válasz)*

Az MLflow-futtatások még nem rögzítik, hogy mely adatokon tanultak. Ebben a gyakorlatban
minden tanítási futtatás címkeként kapja meg az adatverziót, így az általuk használt adatok
alapján kereshetsz futtatásokat. Egy incidens kivizsgálásakor a „melyik futtatás használta
a hibás adatokat?” kérdésre egyetlen lekérdezéssel kell tudni válaszolni.

**Teendők:**

1. Implementáld a `log_data_version` és a `log_dataset_input` függvényt a
   `src/week_04_dvc_introduction/dvc_link.py` fájlban. A TODO-k megnevezik a címkéket
   és a mezőket.
2. Futtasd:
   ```bash
   make link             # forces a fresh training run
   make runs-for-data
   make register && make promote && make trace
   ```

A `make link` a `dvc repro -f -s train` parancsot futtatja: a `-f` kikényszeríti a
szakaszt, a `-s` pedig csak ezt az egy szakaszt kényszeríti. Enélkül a `dvc repro`
helyesen kihagyná a `train` szakaszt, mert semmi sem változott.

**Ellenőrzés:** a munkád ellenőrzéséhez töröld a kihagyási jelölőket a
`tests/test_mlflow_link.py` fájlból, majd futtasd a `uv run pytest tests/test_mlflow_link.py`
parancsot. A stackkel együtt ezt írja ki: `5 passed`.
A `make link` az MLflow digestet a DVC md5-e mellett írja ki: eltérnek. A `make trace`
az md5-öt az `5. Data version` sorban jeleníti meg.

**Elakadtál?**
1. Előadás: „A hash-t tartalmazó címke új kérdést tesz lehetővé” és „Ugyanazon fájl két
   hash-e” · Jegyzetek: „Az adatverzió kapcsolása az MLflow-futtatáshoz”
2. MLflow-dokumentáció: Datasets (a fenti hivatkozáson)
3. Az MLflow-nak átadott `source` értéknek `s3://` URI-nak kell lennie; a `dvc_data_url`
   segédfüggvény egy ilyet ad.

**Írásos válasz** (az `answers.md` fájlban):

1. Az MLflow digestje 8, a DVC md5-e pedig 32 karakteres. Mit hash-elnek? Melyiket
   adnád egy auditornak, aki azt kéri, bizonyítsd be, mely bájtokon tanult a modell?
   Mire jó a másik?
2. Futtasd a `make runs-for-data` parancsot, és írd le az általa használt szűrőkifejezést.
   Melyik olyan kérdésre válaszol, amelyre a 3. héten még nem tudtál?
3. Futtasd a `make trace` parancsot, és hasonlítsd össze a 3. heti kimenettel. Melyik
   sor az új? Most már teljes a lánc, vagy még mindig van egy követhetetlen kapcsolat?

### 7. gyakorlat (opcionális): a még hozzá nem adott adatok felismerése (≈ 10 perc) *(írásos válasz)*

Egy futtatás adatcímkéje csak akkor igaz, ha a lemezen lévő fájl azonos a pointer által
megnevezett fájllal. A munkád során kijavítasz néhány sort, és azonnal újratanítasz,
a `dvc add` előtt. Egy évvel később egy audit az futtatás címkéjében bízik. Ebben a
gyakorlatban látod, ahogy egy futtatás hibás verziót rögzít, majd hozzáadsz egy ellenőrzést,
amely leállítja.

**Teendők:**

1. Nyisd meg a `data/measurements.csv` fájlt a szerkesztődben. Az első beteg sorában
   módosítsd a `bmi` értékét `33.6`-ról `33.7`-re, majd mentsd el.
2. Vizsgáld meg a fájlt úgy, ahogy a 3. héten, majd úgy, ahogy a DVC teszi:
   ```bash
   uv run python src/main.py verify-data          # same name, 768 rows, a new md5
   uv run dvc status data/measurements.csv.dvc    # modified: data/measurements.csv
   ```
   A 3. hét csak a fájl nevét és a sorok számát rögzítette. Mindkettő változatlan.
3. Taníts kézzel, ahogy egy szakasz hibakeresésekor tennéd:
   ```bash
   uv run python src/main.py prepare
   uv run python src/main.py train
   make runs-for-data
   ```
   Hasonlítsd össze a `train` által kiírt `DVC md5` értéket a `verify-data` md5-ével.
   Az új futtatás a 3. verzión tanítottként jelenik meg, valójában azonban a módosításodon
   tanult.
4. Implementáld a `require_data_added` függvényt a `dvc_link.py` fájlban. Futtasd újra a
   `uv run python src/main.py train` parancsot: leáll.
5. Vond vissza a módosításodat, és építsd fel újra:
   ```bash
   uv run dvc checkout --force data/measurements.csv
   make repro
   ```

**Ellenőrzés:** a munkád ellenőrzéséhez töröld a kihagyási jelölőket a
`tests/test_data_added.py` fájlból, majd futtasd a `uv run pytest tests/test_data_added.py`
parancsot. Ezt írja ki: `2 passed`. A 4. lépésben a `train` kiírja, hogy
``Cannot run `train` yet``, és közli, hogy futtasd a `dvc add` parancsot.

**Elakadtál?**
1. Előadás: „Az előző heti adatkövetés hiányos volt” és „Tanítás még hozzá nem adott
   adatokon” · Jegyzetek: „Tanítás még hozzá nem adott adatokon”
2. DVC-dokumentáció: https://doc.dvc.org/command-reference/status
3. A `file_md5` és a `pointer_md5` adja a két összehasonlítandó értéket.

**Írásos válasz** (az `answers.md` fájlban):

1. Mely bájtokon tanult a 3. lépésbeli futtatás, és melyik verziót nevezi meg a címkéje?
   Egy auditor egy évvel később megtalálja ezt a futtatást. Mire következtet, és miért
   rosszabb ez, mint egy adatcímke nélküli futtatás?
2. Az ellenőrzésed a `train` szakaszban fut. Nevezz meg egy másik helyet a csapat
   munkafolyamatában, ahol ugyanez az ellenőrzés futhatna, és mondd el, mibe kerül.

## Befejezés: a munka commitolása és beadása (≈ 5 perc)

Először futtasd a teljes tesztcsomagot: a `uv run pytest tests/` a stackkel együtt
`49 passed, 2 skipped` eredményt ír ki (`51 passed`, ha elvégezted a 7. gyakorlatot),
stack nélkül pedig `44 passed, 7 skipped` eredményt (`46 passed, 5 skipped` a 7. gyakorlattal).

```bash
git status          # answers.md must appear; .env and .venv/ must NOT
git add .
git commit -m "week04: version the dataset with DVC, link it to MLflow, and write up the exercises"
```

Ellenőrizd, hogy **egyik** se jelenjen meg: `.env`, `.venv/`, `.dvc/cache/`,
`.dvc/config.local`, `data/measurements.csv`. Az utolsónak hiányoznia kell: a pointere
tartozik a Gitbe.

Töltsd fel a commitot, nyisd meg a GitHubon
(`https://github.com/<you>/<repo>/commit/<hash>`), és töltsd fel az URL-t a Moodle-ba.

---

## Mi hol található

| Elem | Hol található | Miért |
| --- | --- | --- |
| `data/incoming/batch_*.csv` | Git | a még meg nem érkezett kötegek (szimuláció) |
| `data/raw/batch_*.csv` | Git | a megérkezett kötegek; ezekből épül fel az adathalmaz |
| `data/diabetes.csv` | Git | a változatlan 1–3. heti pillanatkép |
| `data/measurements.csv` | **Silo** (`dvc-storage`) | a verziózott adathalmaz |
| `data/measurements.csv.dvc` | Git | a fenti bájtokat megnevező négy sor |
| `dvc.yaml`, `params.yaml` | Git | amit deklaráltál |
| `dvc.lock` | Git | ami ténylegesen lefutott |
| `metrics/metrics.json`, `models/mlflow_run_id.json` | Git | `cache: false`, ezért megjelennek a diffben |
| `models/model.pkl`, `data/processed/*.csv` | DVC-gyorsítótár / Silo | a folyamat újraépíthető kimenetei |
| `.dvc/config` | Git | a megosztott távoli tárhely definíciója |
| `.dvc/config.local`, `.dvc/cache/`, `.dvc/tmp/` | sehol (git-ignorált) | csak helyi; a `config.local` kulcsokat tarthat |

## Leállítás

```bash
make down      # stop; data and runs stay in the volumes
make down-v    # stop AND delete both buckets and the database
```

## Hibaelhárítás

| Probléma | Megoldás |
| --- | --- |
| `ERROR: failed to initiate DVC - ... is not tracked by any supported SCM tool` | A `dvc init` parancsot `--subdir` nélkül futtattad. Használd a `make dvc-init` parancsot. |
| `NoCredentialsError` / `Unable to locate credentials` a `dvc push` vagy `dvc pull` során | Ennek a terminálnak nincsenek Silo-kulcsai. Ismételd meg a 2. gyakorlat 4. lépését, vagy használd a Makefile-t. |
| A `dvc push` TLS/SSL hibával meghiúsul | A végpont `http://`. Futtasd: `uv run dvc remote modify storage use_ssl false`. |
| A `make repro` azt írja: „didn't change, skipping”, de új MLflow-futtatást szeretnél | Ez helyes: semmi sem változott. Használd a `make link` parancsot. |
| `No batch file in data/raw` | Még nem érkezett köteg. Futtasd a `make next-batch` parancsot (2. gyakorlat). |
| `ERROR: Checkout failed ... Is your cache up to date?` | Ez a verzió nincs a gyorsítótárban. Futtasd a `dvc pull` parancsot (3. gyakorlat). |
| A `dvc checkout` vagy `dvc pull` az 5. gyakorlat előtt hibázik a `data/processed/*.csv` miatt | Nevezd meg a fájlt: `uv run dvc pull data/measurements.csv`. |
| `error: pathspec ... did not match` a 4. gyakorlatban | Abban a commitban nincs pointer. Használd a `git log --oneline -- data/measurements.csv.dvc` által listázott 1. verziós commitot. |
| `Can't remove the following unsaved files without confirmation` | A `dvc checkout` védi a módosításodat. A törléséhez add meg a `--force` kapcsolót (7. gyakorlat). |
| A `dvc status` friss klónozás után `modified` értéket jelez | Sorvégződések (CRLF). A labor `.gitattributes` fájlja LF-et kényszerít; próbáld a `git add --renormalize .` parancsot. |
| `Bind for 0.0.0.0:5500 failed: port is already allocated` | Egy másik heti stack fut. Állítsd le a mappájában a `docker compose down` paranccsal. |
| A `dvc dag` lapozót nyit meg | Nyomd meg a `q` billentyűt. A Makefile ezt a `DVC_PAGER=cat` beállítással kerüli el. |
| Csak egy vödör látható a Silo konzoljában | A `.env` fájlod régebbi ennél a labornál. Állítsd be a `DVC_BUCKET=dvc-storage` értéket, majd futtasd: `make down-v && make up`. |

## Következő lépések

Most már bizonyítani tudod, mely adatokon tanult egy modell. Azt azonban semmi sem
ellenőrizte, hogy az adatok helyesek-e: a `data.require_columns` csak azt vizsgálja,
hogy az oszlopok léteznek-e, és nem séma. A `glucose`, `insulin` és `bmi` oszlopok még
mindig lehetetlen nulla értékeket tartalmaznak. Az 5. hét adat-szerződéseket és
Pandera-alapú validációt ad hozzá.
