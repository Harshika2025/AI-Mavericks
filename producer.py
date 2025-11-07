import json
import time
from confluent_kafka import Producer

EVENTHUB_NAMESPACE = "aimavericks-01.servicebus.windows.net:9093"
SASL_CONNECTION_STRING = "Endpoint=sb://aimavericks-01.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=0GxT1/VGCeNPOVJ75StNeeMGO02kSEwYu+AEhIMWPnQ="

conf = {
    'bootstrap.servers': EVENTHUB_NAMESPACE,
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': "$ConnectionString",
    'sasl.password': SASL_CONNECTION_STRING
}

producer = Producer(conf)

def send_view_event():
    event = {
        "event_id": "view-" + str(int(time.time())),
        "user_id": "user123",
        "product_id": "prod567",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "web"
    }
    producer.produce("ai_mavericks.view", json.dumps(event).encode("utf-8"))
    print("✅ Sent VIEW event:", event)

def send_purchase_event():
    event = {
        "event_id": "purchase-" + str(int(time.time())),
        "user_id": "user123",
        "product_id": "prod567",
        "price": 199.99,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    producer.produce("ai_mavericks.purchase", json.dumps(event).encode("utf-8"))
    print("🛒 Sent PURCHASE event:", event)

if __name__ == "__main__":
    for _ in range(5):
        send_view_event()
        time.sleep(1)
    for _ in range(3):
        send_purchase_event()
        time.sleep(1)
    producer.flush()
