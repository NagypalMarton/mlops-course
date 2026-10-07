# 2. feladat

## The batch has a notes column that the contract does not name. The clinic says it is free text and will come in every batch from now on. Would you add it to the contract, drop it before validation, or keep rejecting the batch? Decide, and say who must agree.

Én nem dobnám el csendben a `notes` oszlopot, mert így az adatforrás változása
észrevétlenül maradhatna, és fontos információ is elveszhetne. Mivel a klinika
ezt az oszlopot mostantól minden batchben küldi, felvenném az ingestion
contractba, de csak akkor, ha az oszlop jelentésében és formátumában
megállapodtunk.

Ehhez legalább az adatot küldő klinikának, az adatplatformért felelős
csapatnak és a modellt használó ML-csapatnak kell egyetértenie. Azt is rögzíteni
kellene, hogy a `notes` csak szabad szöveg-e, lehet-e üres, illetve a későbbi
feldolgozás használja-e. Addig, amíg ez nincs egyeztetve, helyesebb a batch-et
elutasítani, mint automatikusan figyelmen kívül hagyni az új oszlopot.

## List the four faults in the batch: for each, the row, the column and the bad value. The report has 7 lines for 4 faults. Which fault caused more than one line, and why?

1. A **4. adat sorban** (`glucose` oszlop, Pandera-index: **3**) a rossz érték:
   **`unknown`**. Ez nem alakítható számmá.
2. A **8. adat sorban** (`age` oszlop, Pandera-index: **7**) a rossz érték:
   **`250`**. Ez meghaladja a megengedett 120-as maximumot.
3. A **24. adat sorban** (`bmi` oszlop, Pandera-index: **23**) a rossz érték:
   **`280.0`**. Ez meghaladja a megengedett 100-as maximumot.
4. Minden sorban szerepel egy, a szerződésben nem deklarált **`notes`** oszlop,
   amelynek értéke: **`imported from lab system v2`**. Ez a teljes batch
   extra oszlop hibája, nem egyetlen betegérték hibája.

A riport ezért hét hibasort tartalmaz, bár csak négy tényleges hiba van. A
`glucose` mezőben lévő `unknown` két ellenőrzést is megsért: először a Pandera
nem tudja a szöveget `float` típussá alakítani (`coerce_dtype`), majd az
elvárt `float64` adattípus ellenőrzése is hibát jelez. A másik három hiba egy-egy
riportsort eredményez.

# 4. feladat
# Compare the two runs of make gate-fail. Without the gate, which files did the row with age = 250 reach, and who or what would use them next?


# `validate` has failed. A teammate in a hurry runs uv run python src/main.py prepare by hand. What happens, and which line of your code makes it happen? Why is the edge in dvc.yaml not enough on its own?


# You raise MAX_AGE from 120 to 125. Predict which stages make repro runs and which it skips. Try it, then set the value back and run make repro again. Explain why each stage ran or skipped, and say whether the model needed to be trained again.

# 6. feladat