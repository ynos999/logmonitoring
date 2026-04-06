import pika, json, time, os

def process_task(ch, method, properties, body):
    task = json.loads(body)
    print(f"Apstrādā uzdevumu: {task}")
    
    if task['type'] == 'order_created':
        # Simulē e-pasta sūtīšanu
        time.sleep(0.5)
        print(f"E-pasts nosūtīts par pasūtījumu: {task['item']}")
    
    # Paziņo RabbitMQ ka uzdevums pabeigts — izdzēš no rindas
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    while True:
        try:
            conn = pika.BlockingConnection(
                pika.ConnectionParameters(os.getenv('RABBITMQ_HOST', 'rabbitmq'))
            )
            ch = conn.channel()
            ch.queue_declare(queue='tasks', durable=True)
            ch.basic_qos(prefetch_count=1)  # apstrādā vienu uzreiz
            ch.basic_consume(queue='tasks', on_message_callback=process_task)
            print("Worker gatavs — gaida uzdevumus...")
            ch.start_consuming()
        except Exception as e:
            print(f"Savienojuma kļūda: {e} — mēģina vēlreiz pēc 5s")
            time.sleep(5)

if __name__ == '__main__':
    main()