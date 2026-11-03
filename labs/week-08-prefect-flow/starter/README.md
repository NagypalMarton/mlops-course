# 8. heti labor — Prefect flow

A 7. héten a GitHub Actions-t használtad a tesztek és a minőségkapu (quality gate) automatikus futtatására. Az ütemezett
tanítási feladatoknak is szükségük van egy megoldásra, amely rögzíti az állapotukat és jelenti a hibákat. Ezen a laboron
a Prefectet használod a tanítási pipeline futtatására és ütemezésére, az előzmények ellenőrzésére, valamint az újrapróbálások
(retries) beállítására.

## Amivel már rendelkezel

A labor a Compose stackre, az MLflow-ra, a Silóval támogatott DVC-re és az 1–7. hét
`validate → prepare → train → evaluate → gate` pipeline-jára épít. Megtartja mindkét
szerződést, a minőségkaput, a `make ci` célt és mindkét GitHub Actions-munkafolyamatot. A modell, a metrikák
és a küszöbértékek változatlanok maradnak.

Újítások ezen a héten:

- Prefect, az orkestrátor: `prefect==3.8.2`, egy hozzá igazított szerverképpel.
- Egy Prefect-szerver a `compose.yaml` fájlban. Az adatait a meglévő Postgres-konténerben
   található második adatbázisban tárolja.
- `tasks.py` és `flows.py`. A legtöbb feladat (task) már rendelkezésre áll. Ezeket egy flow-ba
    fogod összeállítani, beállítod az újrapróbálásokat, és ellenőrzöd az eredményeket.

A `dvc repro` lefuttatja a pipeline szakaszait, és kihagyja azokat, amelyek bemenetei nem változtak. A Prefect-flow
egyetlen feladatként hívja meg a `dvc repro` parancsot. Emellett hálózati műveleteket futtat, kezeli az újrapróbálásokat és
az ütemezést, valamint rögzíti minden flow- és task-futtatás állapotát.

## Alapok (hivatalos oktatóanyagok)

- **Prefect – gyors kezdés (fő sablon):** https://docs.prefect.io/v3/get-started/quickstart
- **Flow-k és taskok:** https://docs.prefect.io/v3/concepts/flows · https://docs.prefect.io/v3/concepts/tasks
- **Újrapróbálások:** https://docs.prefect.io/v3/how-to-guides/workflows/retries
- **Saját üzemeltetésű szerver:** https://docs.prefect.io/v3/advanced/self-hosted
- **Telepítések és ütemezések:** https://docs.prefect.io/v3/how-to-guides/deployments/create-schedules
- **Flow-k tesztelése (`prefect_test_harness`):** https://docs.prefect.io/v3/how-to-guides/workflows/test-workflows

## Előfeltételek

- Az 1–7. hét működő környezete: `uv`, Docker, Git.
- Ha egy korábbi hét Postgres-kötetét használod újra, az nem fogja tartalmazni a `prefectdb`
  adatbázist. Lásd a Hibaelhárítás című részt.

## Telepítés

```bash
# Állítsd le az összes többi laborstacket; a laborok megosztják az 55xx gazdagépportokat
cd ../../week-07-ci-workflow/starter && make down; cd -

cp .env.example .env
make sync          # telepít minden függőségi csoportot
make up            # elindítja a postgres-, s3-, mc-, mlflow- és prefect-szervereket
make data-v2       # újraépíti a DVC-vel nyomon követett adatkészletet a commitolt nyers kötegekből
make repro         # a 7. hét változatlan pipeline-ja: GO-val kell zárulnia
make prefect-ui    # kiírja a felhasználói felület címét: http://127.0.0.1:5520
```

Nyisd meg a Prefect felhasználói felületét. Még nincsenek benne flow-futtatások.

Futtasd az `uv run pytest -q` parancsot a gyakorlatok megkezdése előtt. Leállított stackkel a várt eredmény:

```
181 passed, 25 skipped
```

A kihagyott tesztek közül 13 a `tests/test_flows.py` fájlban található. Mindegyik előtt egy, az
adott gyakorlatot jelölő `@pytest.mark.skip` található. Töröld a jelölőt, amikor megvalósítod
az általa lefedett kódot, majd futtasd a tesztet. A másik 12 teszt infrastruktúrát igényel. A stack
elindítása után közülük a 8 MLflow-hivatkozást ellenőrző teszt is lefut.

A `tests/test_scope.py` ellenőrzi, hogy a kód nem importál a későbbi hetekben bevezetett eszközöket.
A Prefect némelyiket függőségként telepíti; a teszt engedélyezi, hogy ezek telepítve legyenek.

## Gyakorlatok

Végezd el az öt gyakorlatot sorrendben. A 2. és az 5. gyakorlatra adott válaszaidat ebben a könyvtárban
található `answers.md` fájlba írd, és a fájlt a kódoddal együtt commitold.

### 1. gyakorlat — Taskok és egy flow (`make flow`)

Egy Prefect-task egy munkafolyamat egy lépése. Egy flow meghívja a taskokat, és rögzíti minden futtatás
állapotát, időtartamát és naplóit. A csapat ezt a nyilvántartást használhatja annak megállapítására, hogy
hol hibásodott meg egy tanítási futtatás, és mi készült el a hiba előtt. Ebben a gyakorlatban a megadott
taskokat egy tanítási flow-ba rendezed, majd megvizsgálod annak futtatását a Prefect felületén.

Töltsd ki a `flows.py` fájlban található `training_flow` függvényt. A TODO a taskokat sorrendben felsorolja.
Hívd meg a `notify` függvényt akkor is, amikor a flow sikertelen, és akkor is, amikor sikeres.

Ezután futtasd a `make flow` parancsot, és nyisd meg a futtatást a felületen. Keresd meg a tasklistát,
az egyes taskok állapotát és időtartamát, valamint a `run_pipeline` belsejében futó `dvc repro` naplósorait.

**Ellenőrzés:** távolítsd el a kihagyási jelölőket a `tests/test_flows.py` „A tanítási flow” szakaszában,
és mindkét tesztnek sikeresnek kell lennie. A `make flow` futtatásának vége
`Finished in state Completed()`, a kapu eredménye `GO`, ezt a `reports/last_run.txt` rögzíti,
a metrikáid pedig bájtra pontosan egyeznek a 7. héten kapottakkal. A futtatás minden taskjával együtt
megjelenik a felületen.

### 2. gyakorlat — A DVC és a Prefect feladatai (`make flow-dvc`) — **írásbeli**

A DVC és a Prefect is gráfokként írja le a munkafolyamatokat, de eltérő információkat követ nyomon. A DVC
a pipeline-szakaszokat és azok fájlfüggőségeit követi; a Prefect a flow- és task-futtatásokat rögzíti. Ha egy
csapat mindkettőt használja, el kell döntenie, hogy a munkafolyamat egyes részeit melyik eszköz kezelje.
Ebben a gyakorlatban összehasonlítod a gráfokat, és átgondolod, hogyan osztható fel ez a feladat.

Futtasd a `make flow-dvc` parancsot a DVC-gráf és a Prefect felületének címének kiírásához. Hasonlítsd össze
a DVC-gráf fájlfüggőségeit a Prefect által megjelenített taskokkal és futtatási állapotokkal.

1. Nevezz meg három olyan képességet, amelyet a Prefect biztosít ehhez a laborhoz, a DVC viszont nem,
   valamint egy olyan képességet, amelyet a DVC biztosít, a Prefect pedig nem. Magyarázd el, hogy az egyes
   képességek milyen problémát oldanak meg.
2. A `run_pipeline` egyetlen taskként hívja meg a `dvc repro` parancsot. Mit veszítenél, ha ezt szakaszonként
   egy-egy Prefect-taskkal helyettesítenéd? Mikor lehet hasznos a szakaszokat külön taskokra bontani?

### 3. gyakorlat — Újrapróbálások beállítása (`make flow-retry`)

Egy hálózati kérés átmenetileg meghiúsulhat, majd egy újabb próbálkozásra sikerülhet. Az újrapróbálás
egy késleltetés után ismét lefuttatja a sikertelen taskot. Az exponenciális visszalépés növeli ezt a késleltetést;
a jitter változatossá teszi, így kisebb az esélye, hogy az újrapróbálások egyszerre történnek. Egy művelet
ismétlése nem kívánt hatásokkal is járhat, ezért a csapatnak ki kell választania, mely taskokat biztonságos
újrapróbálni. Ebben a gyakorlatban beállítod és teszteled a hálózati taskok újrapróbálási szabályzatát.

Állítsd be az újrapróbálási szabályzatot a `tasks.py` újrapróbálási szakaszának elején található
`NETWORK_RETRIES` változóban: add meg az újrapróbálások számát, az exponenciális visszalépést és a jittert.
A szabályzat már alkalmazva van a Silóval kommunikáló taskokra. Minden más task maradjon újrapróbálás nélkül.

Válaszolj egy-egy mondatban a `NETWORK_RETRIES` feletti megjegyzésben a következő két kérdésre:

- (a) Miért lehet alkalmatlan a `run_pipeline` esetében a `retries=3` beállítás?
- (b) Az újrapróbálás csak akkor biztonságos, ha ugyanannak a műveletnek a kétszeri futtatása nem okoz
  kárt. Az újrapróbálható taskok közül melyiket **nem** biztonságos megismételni? Mit tenne ott egy
  újrapróbálás, és mennyire véd meg az adott taskban meglévő ellenőrzés?

**Ellenőrzés:**

- Távolítsd el a kihagyási jelölőket a három újrapróbálási szabályzatot ellenőrző tesztről és a két
  harness-tesztről. Ezután futtasd a `make flow-retry` parancsot. A szabályzatteszt ellenőrzi, hogy csak
  a hálózati taskok próbálkoznak újra, legalább kétszer, növekvő késleltetéssel és jitterrel. Az egyik
  harness-teszt kétszer meghiúsul, majd sikerül. A másik minden alkalommal meghiúsul, és az újrapróbálások
  elfogyása után is sikertelen marad. Mindkettő az állapotot és a hívások számát, nem pedig a napló szövegét ellenőrzi.
- *(Opcionális, az éles stacken.)* Futtasd a `docker compose stop s3` parancsot, majd a Silo-ba feltöltő
  `make flow-register` parancsot. Figyeld meg az újrapróbálások közötti késleltetéseket, majd futtasd a
  `docker compose start s3` parancsot.

### 4. gyakorlat — Paraméterek commitban (`make flow-committed`)

A hiperparaméterek hatással vannak a tanítási futtatás által előállított modellre. Az értékek rögzítése
segít a csapatnak a modellek nyomon követésében és összehasonlításában. A hiperparaméterek a `params.yaml`
fájlban találhatók. Kísérletezés közben szerkesztheted a fájlt és futtathatod a pipeline-t; ütemezett
futtatás esetén commitold a paramétereket, hogy a Git rögzítse a konfigurációt. Ebben a gyakorlatban
minden futtatás rögzíti a tanításhoz használt értékeket, és a commitolt paramétereket megkövetelő futtatás
meghiúsul, ha a `params.yaml` nem commitolt módosításokat tartalmaz.

1. Valósítsd meg a `read_params_used` függvényt a `tasks.py` fájlban. A `dvc.lock` rögzíti az egyes
   szakaszok által használt paraméterértékeket. A `train` szakasz értékeit egyetlen szótárként add vissza.
2. Kövesd a `training_flow` 4. gyakorlathoz tartozó TODO-ját. Minden munka előtt ellenőrizd a
   `params_committed` értékét. Ha a `require_committed_params` be van állítva, és a `params.yaml` nem
   commitolt módosításokat tartalmaz, dobj hibát, amely elmagyarázza a javítás módját. A pipeline után
   add át az értékeket és a commit állapotát a `notify` függvénynek.
3. Kísérletezz: a `params.yaml` fájlban módosítsd az `impute_strategy` értékét `median` értékről `mean` értékre, commit nélkül. Futtasd a `make flow` parancsot. A `train`, az `evaluate` és a `gate` újra lefut, a `reports/last_run.txt` pedig a `train.impute_strategy=mean` és a `params.yaml uncommitted` értékkel zárul.
4. Futtasd a `make flow-committed` parancsot. Ez úgy indítja el a flow-t, ahogyan az 5. gyakorlat ütemezett
   futtatása fogja. A flow a `run_pipeline` elindulása előtt meghiúsul, és a `reports/last_run.txt` megadja az okot.
5. Vond vissza a kísérletet a `git restore params.yaml` paranccsal, majd futtasd újra a `make flow` parancsot.
   A rekord szerint `train.impute_strategy=median` és `params.yaml committed`.

Csapatban egy paraméter módosítását pull requestben javasolhatod felülvizsgálatra.

**Ellenőrzés:** távolítsd el a kihagyási jelölőket a `tests/test_flows.py` „Paraméterek commitban” szakaszából
és a `test_notify_records_the_params_and_whether_they_were_committed` tesztről, majd a teszteknek sikeresnek
kell lenniük. A 4. lépésnek a saját hibaüzeneteddel kell meghiúsulnia, az 5. lépés utáni metrikáknak pedig
egyezniük kell a 7. héten kapottakkal.

### 5. gyakorlat — A flow ütemezése (`make serve`) — **írásbeli**

Az ütemezés meghatározza, mikor kezdődjön a tanítás anélkül, hogy valakinek minden alkalommal el kellene
indítania a parancsot. A feladatnak továbbra is hozzá kell férnie az adataihoz, ismert konfigurációra és
az eredménye jelentésének módjára van szüksége. A csapatnak azt is el kell döntenie, mi történjen a betanított
modell kiadása előtt. Ebben a gyakorlatban kiszolgálsz egy ütemezett flow-t, és megvizsgálod annak futtatását.

Valósítsd meg a `scheduled_flow` függvényt a `flows.py` fájlban. Lekéri az aktuális adatokat, majd
`require_committed_params=True` beállítással futtatja a tanítási flow-t. Nem regisztrálja és nem lépteti
elő a modellt. Távolítsd el a kihagyási jelölőt a `tests/test_flows.py` „Az ütemezett flow” szakaszából;
a teszt mindhárom feltételt ellenőrzi.

Futtasd a `make serve` parancsot a flow cron szerinti kiszolgálásához. Az alapértelmezés 5 percenkénti
futtatás; a percenkénti futtatáshoz állítsd be a `CRON='* * * * *'` értéket. Hagyd futni legalább addig,
amíg egy ütemezett futtatás el nem indul. Ellenőrizd a futtatást a felületen, majd állítsd le a folyamatot
Ctrl-C billentyűkombinációval. Jegyezd fel a flow-futtatás nevét és végső állapotát.

1. Elegendő a minőségkapu teljesítése egy ütemezett feladat által tanított modell kiadásához? Milyen
   további ellenőrzéseket vagy jóváhagyásokat követelnél meg, mielőtt a modell eljut a felhasználókhoz?
2. Miről kell értesítést küldeni, és kinek?
3. Mi történjen a **második** egymást követő hiba esetén, aminek az elsőnél még nem kell megtörténnie?
4. Melyik ütemezett feladathoz kapcsolódó hibát nem észlelnék ezek az ellenőrzések és értesítések?

### Befejezés — commitold a munkádat

```bash
git status          # az answers.md legyen benne; a .env és a .venv/ ne
git add labs/week-08-prefect-flow/starter
git commit -m "week08: prefect flow, retries and written answers"
```

Commitold a kódodat és az `answers.md` fájlt. Az `answers.md` tetejére írd az 5. gyakorlat ütemezett
futtatásának nevét és végső állapotát. Ha a `git status` módosítottként jelzi a `params.yaml` fájlt,
akkor a 4. gyakorlat egyik kísérlete még benne van. Commitolás előtt vond vissza a
`git restore params.yaml` paranccsal.

## Make-célok

| Cél | Mit csinál |
| --- | --- |
| `make flow` | a tanítási flow rögzítése a Prefect felületén (1. gyakorlat) |
| `make flow-dvc` | a két gráf egymás melletti megjelenítése (2. gyakorlat) |
| `make flow-retry` | az újrapróbálási tesztek futtatása (3. gyakorlat) |
| `make flow-committed` | a tanítási flow; elutasítja a nem commitolt `params.yaml` fájlt (4. gyakorlat) |
| `make serve` | ütemezett telepítés; felülírás: `CRON=...` (5. gyakorlat) |
| `make flow-register` | a flow `dvc push` paranccsal és regisztrációval, az éles stack ellen |
| `make prefect-ui` | a felület címének kiírása |
| `make test-flows` | az e heti flow-tesztek futtatása |

A 4–7. hét minden célja továbbra is működik, beleértve a `make ci`, `make repro`, `make gate` célokat
és mindkét GitHub Actions-munkafolyamatot.

## Hibaelhárítás

| Tünet | Ok | Javítás |
| --- | --- | --- |
| `No Prefect server at ...` | a stack leállt | `make up` |
| Minden API-hívás 404-et ad | a `PREFECT_API_URL` végéről hiányzik az `/api` | másold át a `.env.example` fájlból |
| A Prefect-konténer ciklikusan újraindul | hiányzik a `prefectdb`; az inicializáló szkript csak a Postgres-kötet **első** létrehozásakor fut le | `make down-v && make up` (ez az MLflow adatait is törli) |
| A `PREFECT_API_DATABASE_CONNECTION_URL` hatástalan | a beállítás neve megváltozott | használd a `PREFECT_SERVER_DATABASE_CONNECTION_URL` változót |
| `Scheduled_FlowModel is not fully defined` | egy flow-paramétert a Prefect nem tud szerializálni | a `training_flow` docstringjében leírtak szerint a flow-aláírásokban csak szövegeket, számokat és logikai értékeket használj |
| A `dvc pull` részletek nélkül meghiúsul | a Siló hitelesítő adatait nem adták át az alfolyamatnak | lásd a `tasks.py` `_dvc_env` részét |
| Egy ütemezett futtatás `params.yaml has uncommitted changes` hibával meghiúsul | egy kísérlet még a `params.yaml` fájlban van | commitold a módosítást, vagy vond vissza a `git restore params.yaml` paranccsal |
| Hiányzik a `data/measurements.csv` | friss klón; az adatkészletet a DVC követi nyomon, nem a Git | `make data-v2` |
| Egy flow-teszt körülbelül 8 másodpercig tart 1 helyett | harness nélkül futtat flow-t, ezért a Prefect ideiglenes szervert indít | használd a `prefect_harness` fixture-t vagy a `task.fn(...)` hívást |
| A port már használatban van | egy másik hét stackje fut | előbb futtasd a `make down` parancsot az adott laborban |

## Beadás

Add be a Befejezés során létrehozott commitot. A kódodat és az `answers.md` fájlt tartalmazza,
az ütemezett futtatás nevével és állapotával a fájl tetején. A `.env` és a `.venv/` ne legyen benne.

## Eltérések az oktatóanyagoktól

1. **A flow meghívja a `dvc repro` parancsot.** A gyors kezdés egyszerű Python-taskokból állít össze
   flow-t. A meglévő DVC-pipeline követi a bemeneteket, és kihagyja a naprakész szakaszokat, ezért a flow
   ezt hívja meg ahelyett, hogy lecserélné a szakaszait.
2. A labor saját üzemeltetésű szervert használ a meglévő Postgres-konténerrel. Az
   `init-prefect-db.sh` szkript egy második adatbázist hoz létre a Postgres-kötet első létrehozásakor.
3. A labor a `.serve()` metódust használja az ütemezett futtatásokhoz. Ez egy folyamatban fut, és nincs
   szüksége munkakészletre, workerre vagy infrastruktúrablokkra.
4. Az újrapróbálási gyakorlatban neked kell kiválasztanod, mely taskokat kell újrapróbálni, és be is
   kell állítanod az újrapróbálási szabályzatot.
5. A tesztek a flow-futtatásokhoz a `prefect_test_harness` eszközt használják, az alapul szolgáló
   függvényt pedig `task.fn(...)` segítségével tesztelik, amikor ez flow indítása nélkül is lehetséges.

A `.env.example` beállításai tartalmazzák az `/api` utótagot a `PREFECT_API_URL` értékében, és a
`PREFECT_SERVER_DATABASE_CONNECTION_URL` változót használják a szerver adatbáziskapcsolatához.
