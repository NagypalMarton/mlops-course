## Exercise 4 - Choose the winner, and defend the choice

### 1. Do F1 and ROC-AUC pick the same winner? If not, why might two reasonable metrics disagree about the same six models?

**Válasz:**

Nem ugyanazt a modellt választják. Az F1 szerint a `rf-n_estimators=300` modell a győztes, az értéke `0.6240`. ROC-AUC alapján viszont a `logreg-C=1.0` modell nyer `0.8320` értékkel.

Ennek az az oka, hogy a két metrika mást mér. Az F1 a konkrét, alapértelmezett döntési küszöb mellett elért precision és recall egyensúlyát méri, míg a ROC-AUC azt mutatja meg, hogy a modell a különböző küszöbök mellett mennyire jól rangsorolja a pozitív és negatív példákat. Ezért egy modell lehet jobb az aktuális osztályozási döntésekben, miközben egy másik modell összességében jobb rangsorolást ad.

### 2. Pick the run you would promote, write down its `run_id`, and justify it in two or three sentences. There is more than one defensible answer; "it has the highest F1" on its own is not one of them. Look at the confusion matrices before you decide.

**Válasz:**

Én ezt a run-t választanám:

- Modell: `rf-n_estimators=300`
- `run_id`: `91d7bfc93731404cb1d07a8192d618ef`
- F1: `0.6240`
- Recall: `0.5821`
- ROC-AUC: `0.8172`

A random forest nemcsak a legmagasabb F1 értéket adta, hanem a teszthalmazon kevesebb false negative hibát is vétett: 28 diabéteszes beteget sorolt tévesen az egészséges kategóriába, míg a logreg C=1.0 modell 32-t. Mivel ebben a feladatban a fel nem ismert diabéteszes esetek különösen fontosak, a jobb recall és a kevesebb false negative miatt ezt a modellt támogatnám, még akkor is, ha a ROC-AUC értéke alacsonyabb a logisztikus regresszióénál.

### 3. Name one thing MLflow recorded about these runs that you did not have to remember.

**Válasz:**

Az MLflow automatikusan rögzítette minden run modellparamétereit, metrikáit és a modellhez tartozó artifactokat. Így például nem kellett külön feljegyeznem, hogy a kiválasztott random forest `n_estimators=300` beállítással futott, milyen F1- és recall-értéket ért el, illetve melyik kódverzióból származott.
