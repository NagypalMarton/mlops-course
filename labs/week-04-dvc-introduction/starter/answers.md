# 2. gyakorlat

## 1. kérdés

**Mit kapott a Git ebben a commitban, és körülbelül hány bájtot? Mit kapott a
Silo? Miért ez a különbség a DVC lényege?**

A Git megkapta a beérkezett `batch_01.csv` fájlt, valamint a körülbelül 102
bájtos `data/measurements.csv.dvc` pointerfájlt. A Silo a tényleges,
körülbelül 19 KB méretű `data/measurements.csv` adatfájlt tárolja.

Ez a DVC lényege: a nagy adatfájl nem kerül közvetlenül a Gitbe, így a
repository kicsi marad, miközben az adat verziója és pontos tartalma követhető.

## 2. kérdés

**Egy csoporttárs ugyanazzal a köteggel futtatja a `make build-data` parancsot,
és bájtpontosan azonos `.dvc` fájlt kap. Nevezz meg két dolgot, amit a
`build_measurements` ennek érdekében tesz, és egyet, ami ezt megtörné.**

A `build_measurements` például azért ad mindig azonos eredményt, mert:

- a batch fájlokat név szerint, rendezett sorrendben olvassa be;
- a CSV-t indexoszlop nélkül és egységes `LF` sorvégekkel írja ki.

Ezt megtörné például, ha a fájlokat véletlenszerű sorrendben fűzné össze, vagy
`index=True` beállítással az indexet is beleírná a CSV-be.

## 3. kérdés

**Egy csapattárs klónozza a tárolót. Megvan neki a
`data/measurements.csv.dvc`, de nincs `data/measurements.csv`. Melyik egyetlen
parancsot futtatja, és melyik két feltételnek kell teljesülnie ahhoz, hogy
működjön?**

A csapattárs ezt a parancsot futtatja:

```powershell
uv run dvc pull data/measurements.csv
```

Ehhez két feltételnek kell teljesülnie:

- A DVC remote helyesen legyen beállítva, és a Silo elérhető legyen.
- A csapattársnak legyenek érvényes Silo/AWS hozzáférési kulcsai, valamint az
  adott adatverzió ténylegesen legyen feltöltve a remote tárhelyre.

# 4. gyakorlat

## 1. kérdés

**Az időutazás két parancsot igényelt. Mit változtatott a lemezen a
`git checkout`, mit változtatott a `dvc checkout`, és miért nem tudja egyik sem
elvégezni a másik feladatát?**

A `git checkout` a Gitben verziókezelt pointerfájlt, vagyis a
`data/measurements.csv.dvc` fájlt állította vissza az 1. verzió állapotára.
Ez csak azt módosítja, hogy a pointer melyik adatverzióra hivatkozik; magát a
nagy adatfájlt nem tölti vissza.

A `dvc checkout` ezután a pointerben megadott hash alapján visszaállította a
helyi `data/measurements.csv` fájlt az 1. verzió tartalmára.

A két parancs azért nem tudja egymás feladatát elvégezni, mert a Git csak a
pointerfájlt kezeli, a tényleges adatfájl a DVC cache-ben vagy a Silo remote-ban
található. A DVC pedig nem módosítja a Git által verziókezelt pointert, csak az
abban hivatkozott adatfájlt állítja elő.

## 2. kérdés

**Ugyanezt az időutazást egy olyan laptopon próbálod végrehajtani, amely soha
nem töltötte le az 1. verziót. Mi történik?**

A `git checkout` sikeresen visszaállítja az 1. verzióhoz tartozó
`.dvc` pointerfájlt, mert azt a Git tárolja. A `dvc checkout` viszont hibával
leáll, mert az 1. verzió adatfájla nincs benne a laptop helyi DVC-cache-ében.

Először le kell tölteni az adatot a Silo-ból:

```powershell
uv run dvc pull data/measurements.csv
```

Ezután a `dvc checkout` már vissza tudja állítani az 1. verzió tényleges
adatfájlját, feltéve, hogy a DVC remote elérhető, és a szükséges Silo/AWS
hozzáférési kulcsok be vannak állítva.

# 5. gyakorlat

## 1. kérdés

**Sorold fel az `evaluate` szakaszod `deps` értékeit. Válassz ki egyet, és
mondd el, mi történik, ha kimarad a listából. A folyamat meghiúsul, vagy lefut
és hibás eredményt ad?**

Az `evaluate` szakasz `deps` értékei:

- `models/model.pkl`
- `models/mlflow_run_id.json`
- `data/processed/test.csv`
- `src/week_04_dvc_introduction/pipeline.py`
- `src/week_04_dvc_introduction/model.py`
- `src/week_04_dvc_introduction/data.py`

Például, ha a `models/model.pkl` kimaradna a listából, a DVC nem tudná, hogy az
`evaluate` szakasz függ a betanított modelltől. Ha a `train` új modellt készít,
a DVC ezért nem feltétlenül futtatná újra az `evaluate` szakaszt, így a metrika
egy régi modell alapján maradhatna. A folyamat tehát lefutna, de hibás vagy
elavult eredményt adna.

## 2. kérdés

**A 3. verzióban ugyanaz a 768 sor található, mint a `data/diabetes.csv`
fájlban. Hasonlítsd össze a `make metrics` eredményét a kurzus rögzített
alapértékével (accuracy 0.7344, F1 0.5785). Eltérnek. Magyarázd meg, hogy
„ugyanazok a sorok” miért nem jelentik azt, hogy „ugyanaz az adathalmaz”.**

A `make metrics` eredménye eltérhet a rögzített alapértékektől, még akkor is,
ha mindkét fájlban 768 sor van. A sorok száma csak a dataset méretét mutatja,
nem a tartalmát. Eltérhetnek például a mérési értékek, a sorok sorrendje, a
duplikátumok, a hiányzó értékek vagy a célváltozó értékei.

Ebben a gyakorlatban a 3. verzió a beérkezett batch fájlokból épül fel, míg a
`data/diabetes.csv` a kurzus korábbi, rögzített snapshotja. Ezért a két fájl
azonos sorszám mellett is más bájtokat és más adatverziót jelenthet. A
train/test felosztás és az ezekből számolt accuracy és F1 értékek emiatt eltérnek
a kurzus alapértékeitől.

# 6. gyakorlat

## 1. kérdés

**Az MLflow digestje 8, a DVC md5-e pedig 32 karakteres. Mit hash-elnek?
Melyiket adnád egy auditornak, aki azt kéri, bizonyítsd be, mely bájtokon tanult
a modell? Mire jó a másik?**

A DVC md5-e a teljes adatfájl bájtjait hash-eli. Ez 32 hexadecimális
karakterből áll, és közvetlenül a `.dvc` pointerben szerepel. Ezt adnám az
auditornak, mert ezzel bizonyítható, hogy pontosan mely adatbájtokat használta
a modell.

Az MLflow digestje az MLflow Dataset-reprezentációjának rövidebb, 8 karakteres
azonosítója. Ez az MLflow-ban az adatbemenet gyors azonosítására és
összehasonlítására használható, de önmagában nem olyan részletes bizonyíték a
teljes fájl tartalmára, mint a DVC md5-e.

## 2. kérdés

**Futtasd a `make runs-for-data` parancsot, és írd le az általa használt
szűrőkifejezést. Melyik olyan kérdésre válaszol, amelyre a 3. héten még nem
tudtál?**

A használt MLflow-szűrőkifejezés:

```text
tags.dvc_md5 = '<aktuális DVC md5>'
```

Ez megkeresi az összes olyan MLflow-futtatást, amely pontosan ezt az adatverziót
használta. Így válaszolható meg például az a kérdés, hogy **mely modellek vagy
futtatások készültek egy adott adatverzióval**, illetve mely futtatások használták
az esetleg hibás adatokat.

## 3. kérdés

**Futtasd a `make trace` parancsot, és hasonlítsd össze a 3. heti kimenettel.
Melyik sor az új? Most már teljes a lánc, vagy még mindig van egy
követhetetlen kapcsolat?**

Az új sor:

```text
5. Data version : <DVC md5>
```

Ez a sor kapcsolja össze az MLflow-futtatást a DVC által azonosított
adatverzióval. A lánc most már eljut a modell aliasától a konkrét adatverzióig:

```text
alias -> modellverzió -> MLflow-run -> Git commit -> DVC md5
```

A lánc az adatfájl tartalmáig technikailag követhető, mert a DVC md5 alapján a
Silo remote-ban megkereshető a megfelelő objektum. Az adat minőségét vagy
helyességét azonban ez még nem bizonyítja; azt a későbbi adatvalidációs
gyakorlatok kezelik.
