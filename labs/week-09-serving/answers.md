# Lab 9 answers
## EXERCISE 1
- Which requests did the server score, and which did it refuse? For each refusal, read the stack trace and find which component detected the problem.
  A szerver besorolta az eredeti, a `glucose=0`, a `glucose=-50`, az `age=250` és
  `bmi=336`, valamint az átrendezett oszlopokat tartalmazó kéréseket. Elutasította
  az extra `cholesterol` oszlopot és a `bmi` oszlop hiányát. Ezeket az MLflow
  pyfunc scoring rétegének input-schema ellenőrzése és nem a modell detektálta;
  az értéktartományokat ez a szerver nem validálta.
- Which of the scored requests should never reach the model? Name the rule from the Week 5 contract that would stop each one.
  A `glucose=0` és `glucose=-50` kérés sérti a Week 5 szerződés `glucose > 0`
  szabályát. Az `age=250` és `bmi=336` kérés az életkorra és BMI-re vonatkozó
  megengedett tartományokat sérti. Ezeket a Pandera-alapú adatkontraktnak kell
  megállítania a modell előtt.
- Name two more things your team would need from a prediction service that this server does not give you.
## Exercise 3
- Online took far longer for the same rows. Where does the time go? Name the steps that a request passes through and the batch call does not.
Az online kiszolgálás azért vett igényben lényegesen több időt (a mérés alapján 68×–101× több időt, mint a batch), mert minden egyes rekord külön HTTP kérésként haladt át a teljes szoftverrétegen. A batch hívás ezzel szemben a memóriában lévő adatmátrixot adja át a modellnek egyetlen vektorizált C/NumPy műveletben. Az online kérésnél az idő a HTTP protokoll és a hálózati keretrendszer kéréskezelési overheadjére, a JSON adat-szerializációra és deszerializációra, a FastAPI útválasztására (routing), valamint a Pydantic és az adatkontraktus által elvégzett egyenkénti típus- és értékvalidációra megy el.
- Give one workload where batch scoring is the right choice, and one where online scoring is. What distinguishes them?
Batch-re példa az éjszakai ajánlórendszer vagy heti churn-elemzés; online-ra a valós idejű bankkártyás csalásfelderítés vagy dinamikus árazás. A fő különbség a válaszidő elvárása (latency vs. throughput) és az adatok rendelkezésre állása: a batch a nagy adatmennyiség kötegelt feldolgozására, az online pedig az azonnali, milliszekundumos válaszidőre optimalizál.
- Why does the table report p50 and p95, and not the mean?
A válaszidők eloszlása jobbra ferde, így az átlagot a ritka, kiugróan lassú kérések (pl. hálózati ingadozás, garbage collection) erősen torzítják. A p50 (medián) a tipikus válaszidőt mutatja meg, a p95 pedig azt a garantált szolgáltatási szintet (SLA-t), amelynél a kérések 95%-a gyorsabb volt.
## EXERCISE 4
- The registry is down when Kubernetes starts a new pod, for example to replace one that crashed. What happens with this image, and with an image that downloads the model from the registry when the container starts?
