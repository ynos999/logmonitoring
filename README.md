# DevOps projekts — Reāllaika žurnālu monitorings

## Palaišana
```bash
docker compose up -d
```

## Web interfeisi
| Serviss                | URL                                     | Lietotājs/Parole|
|------------------------|-----------------------------------------|-----------------|
| Flask                  | http://localhost:5000                   | —               |
| Kibana                 | http://localhost:5601                   | —               |
| RabbitMQ UI            | http://localhost:15672                  | guest/guest     |
| Elasticsearch          | http://localhost:9200                   | —               |
| ClickHouse             | http://localhost:8123                   | —               |
| Prometheus             | http://localhost:9090/targets           | —               |
| Grafana                | http://localhost:3000                   | admin/admin     |
| Cadvisor               | http://localhost:8080/metrics           | —               |
| Node-exporter          | http://localhost:9100/metrics           | —               |
| Elasticsearch-exporter | http://localhost:9114/metrics           | —               |
| Kafka-exporter         | http://localhost:9308/metrics           | —               |

## Testēšanas maršruti
- GET /           — mājas lapa
- GET /order/abc  — izveido pasūtījumu (MongoDB + RabbitMQ)
- GET /error      — simulē kļūdu (redzama Kibana)
- GET /load       — ģenerē 20 nejaušus notikumus

## Datu plūsma
Flask → logs/app.log → Fluentd → Kafka → Logstash → Elasticsearch → Kibana
Flask → MongoDB (pasūtījumi)
Flask → RabbitMQ (uzdevumi)


Atver http://localhost:5601 un seko šiem soļiem:
1. Izveido Data View (ja vēl nav):
Kreisā izvēlne → Stack Management → Data Views → Create data view
Index pattern: app-logs-*
Timestamp: @timestamp
Save
2. Pārbaudi datus Discover:
Kreisā izvēlne → Discover
Izvēlies: app-logs-*
Vajadzētu redzēt dokumentus ar event_type, urgency, msg laukiem
3. Izveido pirmo vizualizāciju:
Kreisā izvēlne → Dashboards → Create dashboard
→ Create visualization
→ Izvēlies: app-logs-*
→ Chart type: Donut
→ Slice by: event_type.keyword
→ Save and return
4. Pievieno otro vizualizāciju — žurnāli laika gaitā:
→ Create visualization (vēlreiz)
→ Chart type: Bar vertical stacked
→ Horizontal axis: @timestamp (Auto interval)
→ Vertical axis: Count of records
→ Break down by: level.keyword
→ Save and return
5. Saglabā dashboard:
→ Save → nosaukums: "App monitorings"
Sūti dažus datus kamēr dari — lai grafikos būtu kas redzams:
→ Invoke-WebRequest -Uri "http://127.0.0.1:5000/load" -UseBasicParsing
→ Invoke-WebRequest -Uri "http://127.0.0.1:5000/order/keyboard" -UseBasicParsing
→ Invoke-WebRequest -Uri "http://127.0.0.1:5000/order/monitor" -UseBasicParsing
→ Invoke-WebRequest -Uri "http://127.0.0.1:5000/order/mouse" -UseBasicParsing
→ Invoke-WebRequest -Uri "http://127.0.0.1:9200/app-logs-*/_search?q=event_type:purchase&pretty" -UseBasicParsing | Select-Object -ExpandProperty Content
6. Notestēt vai prometheus redz servisus:
→ docker exec -it prometheus curl http://prometheus:9090/-/ready
→ docker exec -it prometheus curl http://cadvisor:8080/metrics
→ docker exec -it prometheus curl http://kafka-exporter:9308/metrics
→ docker exec -it prometheus curl http://elasticsearch-exporter:9114/metrics
→ docker exec -it prometheus curl http://node-exporter:9100/metrics

## Paskaidrojumi:
**Logstash** ir rīks, kas paredzēts datu savākšanai, apstrādei un nosūtīšanai uz citām sistēmām (visbiežāk uz Elasticsearch).

**Fluentd** ir atvērtā koda datu (īpaši logu) savācējs un maršrutētājs, kas palīdz apkopot datus no dažādiem avotiem un nosūtīt tos uz citām sistēmām.

**Elasticsearch** ir izkliedēta meklēšanas un analītikas sistēma, kas ļauj ātri meklēt, analizēt un apstrādāt lielus datu apjomus.

**Kibana** ļauj skatīties, analizēt un vizualizēt datus, kas glabājas Elasticsearch.

**ClickHouse** ir ļoti ātra, kolonnveida datubāze, kas paredzēta lielu datu apjomu analīzei reāllaikā (OLAP — Online Analytical Processing).

**MongoDB** ir populāra NoSQL datubāze, kas glabā datus nevis tabulās (kā klasiskās SQL datubāzes), bet gan dokumentos (JSON līdzīgā formātā).

**RabbitMQ** ir ziņojumu starpnieks (message broker) — rīks, kas palīdz dažādām sistēmas daļām savā starpā sazināties, izmantojot ziņojumus (messages).

**Apache Kafka** ir sistēma, kas paredzēta lielu datu plūsmu (event stream) apstrādei reāllaikā.

**ZooKeeper** ir “koordinators” vai “tiesnesis”, kas nodrošina, ka visi serveri sadalīti sistēmā un darbojas saskaņoti.

**Grafana** ir vizualizācija (UI). Parāda datus dashboardos (grafiki, tabulas).
Datus neglabā!
Lasa no: Prometheus (metrikas), Loki (logi), Elasticsearch (logi)

**Prometheus** ir metriku datubāze. Ik pēc X sekundēm scrape (nolasa) metriku endpointus un glabā time-series datus. Ir savs query valoda: PromQL

**Cadvisor** ir konteineru metriku avots. Dod datus par Docker konteineriem: CPU, RAM, Network, Disk.

**Node-exporter** ir servera metriku avots. Dod OS līmeņa metriku: CPU load, RAM, Disk, Network

**Loki** ir logu datubāze (Grafana logs). Glabā logus (kā Elasticsearch, bet vieglāks). Optimizēts tikai logiem un strādā ar Grafana.

**Promtail** ir logu savācējs. Nolasa log failus un sūta uz Loki.

**Elasticsearch-exporter** ir metriku adapteris Elasticsearch. Elasticsearch pats nedod Prometheus formātā metriku. Exporter to pārvērš uz /metrics.

**Kafka-exporter** ir kafka metriku adapteris. Dod info: topic count, consumer lag, broker status.

Visi šie rīki (Elasticsearch, Kibana, Logstash, Fluentd, Apache Kafka, RabbitMQ, ClickHouse, MongoDB) pieder pie modernas backend / datu infrastruktūras.

apps → Kafka / RabbitMQ → processing (Logstash / Fluentd)
     → storage (ClickHouse / MongoDB / Elasticsearch)
     → visualization (Kibana)

| Loma                              | Rīki                                                                                 |
| --------------------------------- | ------------------------------------------------------------------------------------ |
| **Datu savākšana (logs)**         | Fluentd, Logstash, Promtail                                                          |
| **Datu savākšana (metrics)**      | Prometheus (scrape), cAdvisor, Node Exporter, Elasticsearch-exporter, Kafka-exporter |
| **Datu transportēšana**           | Apache Kafka, RabbitMQ                                                               |
| **Datu apstrāde (ETL)**           | Logstash, Fluentd                                                                    |
| **Datu glabāšana (logs)**         | Elasticsearch, Loki                                                                  |
| **Datu glabāšana (metrics)**      | Prometheus                                                                           |
| **Datu glabāšana (biznesa dati)** | MongoDB, ClickHouse                                                                  |
| **Vizualizācija (logs)**          | Kibana, Grafana                                                                      |
| **Vizualizācija (metrics)**       | Grafana                                                                              |
| **Koordinācija**                  | ZooKeeper                                                                            |
| **Monitoring stack**              | Prometheus, Grafana, cAdvisor, Node Exporter, Exporters                              |
| **Secure**                        | Trivy, SonarQube                                                                     |

Sistēma savāc logus un metriku no aplikācijas un infrastruktūras, transportē tos caur Kafka/RabbitMQ, apstrādā ar Logstash/Fluentd, glabā Elasticsearch, Loki un Prometheus, un vizualizē ar Grafana un Kibana.