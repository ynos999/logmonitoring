import logging, json, time, random
from flask import Flask, jsonify
from pymongo import MongoClient
import pika, os

app = Flask(__name__)

# JSON žurnāls — Fluentd to lasa
logging.basicConfig(
    filename="/app/logs/app.log",
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}'
)

def get_mongo():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://mongo:27017/myapp"))
    return client.myapp

def send_to_rabbitmq(task):
    try:
        conn = pika.BlockingConnection(pika.ConnectionParameters(os.getenv("RABBITMQ_HOST","rabbitmq")))
        ch = conn.channel()
        ch.queue_declare(queue="tasks", durable=True)
        ch.basic_publish(exchange="", routing_key="tasks", body=json.dumps(task))
        conn.close()
    except Exception as e:
        logging.error(f"RabbitMQ kļūda: {e}")

@app.route("/")
def index():
    logging.info("Mājas lapa apmeklēta")
    return jsonify({"status": "ok", "message": "DevOps projekts"})

@app.route("/order/<item>")
def order(item):
    db = get_mongo()
    order_doc = {"item": item, "ts": time.time(), "status": "new"}
    result = db.orders.insert_one(order_doc)
    logging.info(f"Pasūtījums: {item} id={result.inserted_id}")
    send_to_rabbitmq({"type": "order_created", "item": item})
    return jsonify({"order_id": str(result.inserted_id), "item": item})

@app.route("/error")
def trigger_error():
    logging.error("Simulēta kļūda — 500")
    return jsonify({"error": "kaut kas nogāja greizi"}), 500

@app.route("/load")
def load_test():
    """Ģenerē nejaušus žurnālus slodzes testēšanai"""
    events = ["pieslēgšanās","meklēšana","pirkums","atteikšanās"]
    for _ in range(20):
        logging.info(f"Notikums: {random.choice(events)} lietotājs={random.randint(1,100)}")
    return jsonify({"status": "ģenerēti 20 notikumi"})

if __name__ == "__main__":
    import os; os.makedirs("/app/logs", exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
