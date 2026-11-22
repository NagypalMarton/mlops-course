# Week 11 written answers

## Instrument the service

### A teammate opens a pull request that adds the patient's age as a label on model_predictions_total to show predictions by age. Would you approve it? Estimate how many series it would add and say where else this information could go.

Nem hagynám jóvá az `age` label hozzáadását a `model_predictions_total`
metrikához.

Az életkor korlátlan/kis előre nem látható kardinalitású jellemző a
metrikákban: minden megfigyelt egész vagy tizedes életkorérték külön
labelértéket hozna létre. A Pima-adatkészletben 52 különböző életkor szerepel
a 21–81 tartományban. A két `outcome` értékkel együtt ez körülbelül
`52 × 2 = 104` predikciós time series lenne, vagyis 102-vel több, mint a jelenlegi
2 outcome sorozat. Új életkorok megjelenésével a szám tovább nőne.

Az életkor inkább logokban vagy trace/request-metadata-ként használható az
egyedi predikciók diagnosztizálásakor, illetve szükség esetén korlátozott,
aggregált jelentésben (például `age_band="18-29"`). Az életkor-bucketeket
szándékosan és kis elemszámban kell kialakítani, valamint az adatvédelmi
következményeket is felül kell vizsgálni.

## Scrape the service and query it
### Next month the API runs as three replicas. A colleague wants the dashboard to show the mean of the three replicas' p95 latency. Would you accept it? Write the query you would use instead and say why it gives the right answer.

Nem fogadnám el a három replikán számolt p95 értékek átlagát. Mindegyik p95
az adott replica saját késleltetési eloszlásából számított percentilis, és
ezek átlagolása nem állítja helyre a teljes flotta percentilisét.

Először össze kell adni a replikák histogram-bucketjeit az `le` label
szerint, majd az összesített bucket-rate-ekre kell alkalmazni a
`histogram_quantile` függvényt:

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)
```

A replikák bucket-számlálóinak összeadása megőrzi a teljes flotta
késleltetési eloszlását, így a Prometheus a valódi p95-öt számolja ki ahelyett,
hogy három külön, közelítő p95 érték átlagát venné.

## Read the SLO and watch an alert fire
### The product owner asks for 99.9% availability instead of 99%. Would you accept it for this service? Give the error budget in minutes per 30 days from your run and explain your decision.

Nem fogadnám el automatikusan a 99,9%-os rendelkezésre állást anélkül, hogy
volna bizonyíték arra, hogy a szolgáltatás ezt fenntartani tudja.

A 99,9%-os rendelkezésre állási SLO 0,1% kiesést engedélyez, ami 30 nap alatt
43,2 perc. A 99%-os cél 432 percet enged, vagyis tízszer több kiesést.

A traffic-futás során 267 darab `200` és 33 darab `422` státuszú válasz készült.
A `422` válaszok tudatos szerződés-elutasítások, ezért nem fogyasztják a
rendelkezésre állási hibaköltségkeretet; csak az 5xx válaszok és a szolgáltatás
kiesései érinthetik azt.

99,9%-ot csak akkor fogadnék el, ha a mért 5xx- és szolgáltatás-kiesési adatok,
beleértve a replikák viselkedését is, elegendő bizonyítékot adnának arra, hogy
a szolgáltatás 30 nap alatt a 43,2 percnyi elérhetetlenségi kereten belül marad.