# 2. feladat
## Meg tudod nevezni a legrosszabb csoportot, annak n értékét, és össze tudod vetni a ROC AUC-jét az összesített 0.8345 értékkel.

A legrosszabb teljesítményt mutató alcsoport az `age_band` szelet `50+` csoportja: a ROC AUC mindössze **0.6071**, ami **0.2274-gyel elmarad** az összesített 0.8345-ös értéktől ($n = 19$). Ugyanebben a csoportban az FPR 0.4167 (a `21-29`-es csoport 0.0685-ös értékéhez képest +0.3482).

A kis elemszám ($n = 19$) miatt ez az eltérés nem feltétlenül jelent modellhibát; üzleti vagy fejlesztési döntés előtt több adatgyűjtés és újabb tesztelés szükséges.

# 4. feladat
## Az 5. heti kapu azért működött, mert a prepare függött az eredményfájltól. Miért nem működhet ez ennél a kapunál, és mi helyettesíti?

Az 5. héten a `prepare` közvetlenül függött a verdict fájltól, ezért a DVC automatikusan
megállította a folyamatot, ha az adatkapu NO-GO eredményt írt. Ennél a kapunál viszont a
`gate` az utolsó szakasz, tehát a `register` és a `promote` nem lehetnek tőle függő DVC
szakaszok. Ha azok függnének a `gate` kimenetétől, a modellregisztráció és a promotálás
nem lenne normális, külön kiadható művelet. Ezt ezért a `require_go` függvény helyettesíti:
kiolvassa a `reports/gate.json` fájlt, és csak rögzített GO verdict esetén engedi a modellt
regisztrálni vagy stagingbe léptetni.

## Mi történik, ha a register nem hívja meg a require_go függvényt? Ki és mikor veszi ezt észre?

Ha a `register` nem hívja meg a `require_go` függvényt, akkor egy NO-GO vagy még nem
ellenőrzött modell is bekerülhet az MLflow modellregiszterbe. Ezt nem feltétlenül veszi
észre azonnal senki, mert a regisztráció technikailag sikeresnek látszik. A probléma akkor
derül ki, amikor valaki később stagingbe vagy éles környezetbe próbálja léptetni a modellt,
vagy amikor egy audit megvizsgálja a kiadási folyamatot. A `require_go` már a regisztráció
előtt megakadályozza ezt, ezért a hibás modell nem jut tovább.

## C: 0.005 mellett az F1 0.1098-cal csökkent, a ROC AUC pedig nőtt. Melyik a helyes válasz? Mit kell tudnod a modell használatáról, és mire kötelez az acceptance.regression.primary_metric?

Nincs minden helyzetben egyetlen helyes metrika. A ROC AUC azt mutatja meg, hogy a modell
mennyire jól rangsorolja a pozitív és negatív eseteket, az F1 viszont a választott
0.5-ös döntési küszöbnél kapott osztályozások minőségét méri. Ezért előfordulhat, hogy a
ROC AUC nő, miközben az F1 csökken, például ha a valószínűségek sorrendje javul, de kevés
érték lépi át a pozitív döntési küszöböt.

Ahhoz, hogy eldöntsük, melyik fontosabb, tudnunk kell, hogyan használják a modellt: rangsorol
vagy döntést hoz, mennyire költségesek a téves pozitív és a kihagyott pozitív esetek, illetve
van-e lehetőség a döntési küszöb módosítására. Ebben a projektben az
`acceptance.regression.primary_metric` értéke `f1`, ezért a regressziós kapu az F1-et tekinti
elsődlegesnek. A `C: 0.005` modell így akkor is megbukhat, ha a ROC AUC javult, mert az F1
0.1098-cal visszaesett.

# 5. feladat
## Az age_band kiválasztási ráta különbsége 0.30 fölött van, mégis csak a TPR-különbségét kapuzod. Miért védhető a nagy kiválasztási ráta különbsége?

A kiválasztási ráta azt mutatja, hogy az egyes csoportokból milyen arányban kapnak
pozitív előrejelzést, de önmagában nem mondja meg, hogy ezek a döntések helyesek-e.
Az `age_band` csoportjai eltérő kockázatúak lehetnek, ezért egy nagyobb kiválasztási
ráta-különbség akár a valós kockázati különbségeket is tükrözheti. Emiatt itt inkább
azt kapuzzuk, hogy a valóban pozitív eseteket, vagyis a betegeket, hasonló arányban
találja-e meg a modell. Ez a TPR-különbség, és az egészségügyi alkalmazásban
közvetlenebbül kapcsolódik a kihagyott betegek kockázatához.

## Az `age_band` TPR-határértéke lazább, mint az `insulin_missing` értéke. Miért, és mi késztetne a szigorítására?

Az `age_band` esetében lazább határérték azért lehet indokolt, mert az életkor valódi
kockázati tényező lehet, és az életkori csoportok között eleve lehetnek különbségek.
Az `insulin_missing` viszont egy mérési vagy adatminőségi állapotot jelöl, ezért ott
kevésbé szeretnénk, hogy a hiányzó adat miatt romoljon egy csoport felismerési aránya.
Szigorítást indokolna, ha több mérésen vagy nagyobb adathalmazon is tartósan megmaradna
a TPR-különbség, ha valamelyik csoportban sok valódi pozitív esetet hagyna ki a modell,
vagy ha az üzleti, egészségügyi vagy etikai kockázat miatt a mostani eltérés már nem
lenne elfogadható.

## Ez az adathalmaz nem tartalmaz nemre, etnikumra, jövedelemre vagy klinikára vonatkozó oszlopot. Nevezz meg egy csoportot, amelyre auditálni szeretnéd a modellt, de nem tudod. Minek kellett volna megtörténnie, és mikor?

Én például a nemek szerinti csoportokra is auditálnám a modellt, de ezt az adathalmazból
nem lehet megtenni, mert nincs benne erre vonatkozó oszlop. Már az adatgyűjtés és az
adatmodell megtervezésekor fel kellett volna venni ezt az adatot, természetesen megfelelő
adatvédelmi és hozzájárulási szabályok mellett. Ezt még a modell tanítása és az éles
használat előtt kellett volna ellenőrizni, mert utólag a hiányzó csoportokra nem lehet
megbízható fairness-mérést készíteni.