from azure.storage.blob import BlobServiceClient

CONNECTION_STR = "DefaultEndpointsProtocol=https;AccountName=producttrendstorage2025;AccountKey=ODlteOmY3kA1ElkbXF3GKPj4kp1qXet9von78KhS2X6x2skX1hqpRopAhLkx83VcJkl39/gDq27f+AStBsqMoQ==;EndpointSuffix=core.windows.net"
CONTAINER = "snapshots"
BLOB_PATH = "purchase/dt=2025-10-25/part-1761399306.parquet"  # latest snapshot

blob_service = BlobServiceClient.from_connection_string(CONNECTION_STR)
container_client = blob_service.get_container_client(CONTAINER)
blob_client = container_client.get_blob_client(BLOB_PATH)

with open("purchase_snapshot.parquet", "wb") as file:
    file.write(blob_client.download_blob().readall())

print("✅ Purchase snapshot downloaded successfully → purchase_snapshot.parquet")
