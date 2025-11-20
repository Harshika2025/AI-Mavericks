import json
import time
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from confluent_kafka import Consumer, KafkaException

# ===============================
# CONFIGURATION
# ===============================

EVENTHUB_NAMESPACE = "aimavericks-01.servicebus.windows.net:9093"
SASL_CONNECTION_STRING = "Endpoint=sb://aimavericks-01.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=0GxT1/VGCeNPOVJ75StNeeMGO02kSEwYu+AEhIMWPnQ="
CONSUMER_GROUP = "$Default"

STORAGE_ACCOUNT_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=producttrendstorage2025;AccountKey=ODlteOmY3kA1ElkbXF3GKPj4kp1qXet9von78KhS2X6x2skX1hqpRopAhLkx83VcJkl39/gDq27f+AStBsqMoQ==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "snapshots"

BATCH_INTERVAL_SECONDS = 5
VIEW_TOPIC = "ai_mavericks.view"
PURCHASE_TOPIC = "ai_mavericks.purchase"

# ===============================
# SETUP AZURE BLOB CLIENT
# ===============================
blob_service_client = BlobServiceClient.from_connection_string(STORAGE_ACCOUNT_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# ===============================
# KAFKA CONSUMER CONFIG
# ===============================
conf = {
    'bootstrap.servers': EVENTHUB_NAMESPACE,
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': "$ConnectionString",
    'sasl.password': SASL_CONNECTION_STRING,
    'group.id': CONSUMER_GROUP,
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe([VIEW_TOPIC, PURCHASE_TOPIC])

# Buffers for batching
view_events = []
purchase_events = []
last_flush_time = time.time()

# ===============================
# SCHEMA VALIDATION
# ===============================
def is_valid_view(event):
    required = ["event_id", "user_id", "product_id", "timestamp"]
    return all(field in event and event[field] for field in required)

def is_valid_purchase(event):
    required = ["event_id", "user_id", "product_id", "price", "timestamp"]
    return all(field in event and event[field] for field in required)

# ===============================
# FLUSH FUNCTION
# ===============================
def flush_to_azure(topic_name, event_buffer):
    """Write buffered events to Parquet and upload to Azure Blob Storage"""
    if not event_buffer:
        return

    today = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"part-{int(time.time())}.parquet"
    path = f"{topic_name}/dt={today}/{filename}"

    # Convert to parquet in-memory
    table = pa.Table.from_pylist(event_buffer)
    pq.write_table(table, "/tmp/temp.parquet")

    # Upload to Azure Blob
    blob_client = container_client.get_blob_client(path)
    with open("/tmp/temp.parquet", "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

    print(f"[✔] Snapshot uploaded for {topic_name} → {path}")
    event_buffer.clear()

# ===============================
# MAIN LOOP
# ===============================
print("✅ Stream ingestor is running... Waiting for messages...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"[Kafka Error] {msg.error()}")
            continue

        try:
            event = json.loads(msg.value().decode("utf-8"))
            topic = msg.topic()

            if topic == VIEW_TOPIC:
                if is_valid_view(event):
                    view_events.append(event)
                else:
                    print(f"[✘] Invalid VIEW event dropped: {event}")

            elif topic == PURCHASE_TOPIC:
                if is_valid_purchase(event):
                    purchase_events.append(event)
                else:
                    print(f"[✘] Invalid PURCHASE event dropped: {event}")

        except Exception as e:
            print(f"[✘] JSON parsing failed: {e}")

        # Time-based flush
        if time.time() - last_flush_time >= BATCH_INTERVAL_SECONDS:
            print("[⏳] Time reached, flushing snapshots...")
            flush_to_azure("view", view_events)
            flush_to_azure("purchase", purchase_events)
            last_flush_time = time.time()

except KeyboardInterrupt:
    print("\n🛑 Stopping ingestor gracefully...")
finally:
    consumer.close()
