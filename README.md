# DevOps projekts — Reāllaika žurnālu monitorings

## Palaišana
```bash
docker compose up -d
```

## Web interfeisi
| Serviss       | URL                        | Lietotājs/Parole |
|---------------|----------------------------|-----------------|
| Flask lietotne | http://localhost:5000      | —               |
| Kibana         | http://localhost:5601      | —               |
| RabbitMQ UI    | http://localhost:15672     | guest/guest     |
| Elasticsearch  | http://localhost:9200      | —               |
| ClickHouse     | http://localhost:8123      | —               |

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

Invoke-WebRequest -Uri "http://127.0.0.1:5000/load" -UseBasicParsing
Invoke-WebRequest -Uri "http://127.0.0.1:5000/order/keyboard" -UseBasicParsing
Invoke-WebRequest -Uri "http://127.0.0.1:5000/order/monitor" -UseBasicParsing
Invoke-WebRequest -Uri "http://127.0.0.1:5000/order/mouse" -UseBasicParsing

Invoke-WebRequest -Uri "http://127.0.0.1:9200/app-logs-*/_search?q=event_type:purchase&pretty" -UseBasicParsing | Select-Object -ExpandProperty Content

http://localhost:9090/targets

docker exec -it prometheus curl http://prometheus:9090/-/ready
docker exec -it prometheus curl http://cadvisor:8080/metrics
docker exec -it prometheus curl http://kafka-exporter:9308/metrics
docker exec -it prometheus curl http://elasticsearch-exporter:9114/metrics
docker exec -it prometheus curl http://node-exporter:9100/metrics

Invoke-WebRequest -Uri "http://127.0.0.1:9200/app-logs-*/_search?q=event_type:purchase&pretty" -UseBasicParsing | Select-Object -ExpandProperty Content