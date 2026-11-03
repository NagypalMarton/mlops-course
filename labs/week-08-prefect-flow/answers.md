premium-anaconda, Completed
# TASK2
- Name three capabilities Prefect provides for this lab that DVC does not, and one capability DVC provides that Prefect does not. Explain which problem each capability solves.

  A Prefect rögzíti a flow-k és a taskok futtatásait, így később látható, hogy egy tanítás mikor futott le, mennyi ideig tartott, melyik lépés sikerült, és hol történt hiba. Emellett kezeli az újrapróbálásokat hálózati hibák esetén, például exponenciális késleltetéssel és jitterrel, így egy átmeneti szolgáltatáshiba nem feltétlenül szakítja meg végleg a futtatást. Harmadik képessége az ütemezés és a futtatások felügyelete: a Prefect képes a flow-t cron szerint elindítani, a futási állapotot pedig a felületén megmutatni. Ezek a képességek az üzemeltetési és megfigyelési problémákat oldják meg, amelyekre a DVC önmagában nem ad választ.

  A DVC ezzel szemben a pipeline szakaszait és a fájlfüggőségeket követi nyomon, valamint a bemenetek hash-e alapján eldönti, mely szakaszokat kell újra lefuttatni. Ez biztosítja a reprodukálhatóságot és elkerüli a változatlan szakaszok felesleges újrafuttatását; ezt a tartalom-alapú függőségkövetést a Prefect nem helyettesíti.

- `run_pipeline` calls `dvc repro` as a single task. What would you lose by replacing it with one Prefect task per DVC stage? When might splitting the stages into separate tasks be useful?

  Elveszítenénk a DVC tartalom-alapú döntéseit és a pipeline egységes kezelését, miközben két külön ütemező próbálná irányítani ugyanazt a gráfot. Külön Prefect-taskokra bontás akkor lehet hasznos, ha az egyes szakaszokat önállóan szeretnénk naplózni, újrapróbálni, párhuzamosítani vagy külön erőforrásokon futtatni.

# TASK5
- Is passing the quality gate enough to release a model trained by a scheduled job? What other checks or approvals would you require before it reaches users?

  Nem. A minőségkapu mellett ellenőrizném az adatok frissességét és sémáját, összehasonlítanám a modellt a jelenlegi éles modellel, majd manuális jóváhagyást és fokozatos kiadást kérnék.

- What should be notified, and to whom?

  Értesíteni kellene a futtatás sikeréről vagy hibájáról, a metrikákról, az adatok és a paraméterek állapotáról, valamint a modell kiadhatóságáról. Hiba esetén a fejlesztői vagy ML-platformcsapat kapjon riasztást, jó eredmény esetén pedig a modellgazda és az üzleti felelős.

- What should happen on the second failure in a row that should not happen on the first?

  A második egymást követő hibánál érdemes leállítani a további ütemezett futtatásokat, eszkalálni az esetet, és manuális kivizsgálást kérni, nem pedig automatikusan új modellt kiadni.

- Which scheduled-job failure would these checks and notifications still miss?

  Ezek az ellenőrzések nem feltétlenül észlelik, ha a pipeline technikailag sikeres, de hibás vagy elavult adatokat használ, ezért a modell metrikái elfogadhatók maradnak, miközben az üzleti viselkedése rossz.